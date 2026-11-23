"""Offline actual OpenAIProvider.next_turn payload builder, with a capture client."""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import fraudlens.investigation.provider as provider_module
from fraudlens.bridge_reader import BridgeReader
from fraudlens.investigation.context import outbound_context
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import canonical
from fraudlens.investigation.provider import OpenAIProvider, ProviderError
from fraudlens.investigation.retrieval import SearchResult
from fraudlens.investigation.tools import ToolExecutor, definitions, facts
from fraudlens.scoring.local_contributions import compute_local_contributions
from fraudlens.scoring.model_scorer import FeatureStore, ModelScorer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend/tests/proposals'))
from local_contribution_sidecar import build_sidecar  # noqa: E402

BRIDGE_SHA = '16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004'
PREFIX = 'ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:'


class Captured(Exception):
    pass


class CaptureClient:
    def __init__(self):
        self.responses = SimpleNamespace(with_streaming_response=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        raise Captured


def prompt_v6():
    names = ('investigation-v6.md', 'semantic-worker-addendum-v1.md',
             'report-parallel-history-v1.md', 'report-source-sections-v1.md')
    return '\n\n'.join((ROOT / 'prompts/application' / name).read_text(encoding='utf-8')
                       for name in names)


def tool_results(executor, sidecar=None, compact_text=False):
    case_items, case_result = executor._case()
    if sidecar is not None:
        body = json.loads(case_items[0]['text'])
        body['contribution_summary'] = sidecar
        text = ('Exact case and contribution facts are in the path/value list; synthetic benchmark, '
                'human review required.' if compact_text else canonical(body).decode())
        item = executor._item('case_fact', text, facts(body))
        case_result = executor._result([item], 1, 1, False)
    histories = [executor._history(side)[1] for side in ('sender', 'receiver')]
    if compact_text:
        for i, result in enumerate(histories):
            original = executor._history(('sender', 'receiver')[i])[0][0]
            item = executor._item('history',
                'Exact bounded history facts are in the path/value list; cutoff is exclusive.',
                original['facts'], original['returned_count'], original['eligible_count'],
                original['truncated'], history=original['history'])
            histories[i] = executor._result([item], item['returned_count'],
                                            item['eligible_count'], item['truncated'])
    return [case_result, *histories, procedure_result(executor)]


def procedure_result(executor):
    passages = executor.knowledge.passages(executor.corpus)
    selected = [p for p in passages if (p['document']['title'], p['section']) in {
        ('Simulated review and escalation', 'Review'),
        ('Simulated missing and conflicting facts', 'Missingness')}]
    assert len(selected) == 2
    found = SearchResult(dict(hits=[dict(passage=p) for p in selected]))
    found.truncated = False
    return executor._search('review and missing facts', found)[1]


async def measure(context, results, summary, joined_notice=False):
    provider = object.__new__(OpenAIProvider)
    provider.model = 'gpt-6-luna'
    provider.prompt = prompt_v6()
    provider.parallel_tools = True
    provider.strict_case_sections = True
    provider.reasoning_effort = 'low'
    provider.output_token_cap = 8192
    provider.request_timeout_cap = 60
    provider.transport = SimpleNamespace()
    provider.client = CaptureClient()
    run_id = 'inv_' + 'a' * 32
    projected = outbound_context(context, run_id)
    if joined_notice:
        projected['notice'] = ('Synthetic benchmark; published v2 explanation was unavailable. '
            'A separately verified local log-odds contribution sidecar is available through case facts. '
            'Contributions are not causal findings or a calibrated probability.')
    names = ('get_case_facts', 'get_account_history', 'get_account_history', 'search_procedures')
    arguments = ({}, {'account_side': 'sender'}, {'account_side': 'receiver'},
                 {'query': 'review and missing facts'})
    messages = [dict(type='context', data=projected)]
    history = [dict(role='user', content=canonical(projected).decode())]
    for i, (name, args, result) in enumerate(zip(names, arguments, results, strict=True)):
        call_id = f'call_{i:02d}'
        messages.append(dict(type='tool_call', call_id=call_id, name=name, arguments=args))
        messages.append(dict(type='tool_result', call_id=call_id, result=result))
        history.append(dict(type='function_call', call_id=call_id, name=name,
                            arguments=canonical(args).decode()))
        history.append(dict(type='function_call_output', call_id=call_id,
                            output=canonical(result).decode()))
    provider.history, provider.seen = history, len(messages)
    sizes = {}
    original = provider_module.canonical

    def measuring(value):
        encoded = original(value)
        if isinstance(value, dict) and 'input' in value and 'tools' in value:
            sizes['request_bytes'] = len(encoded)
            sizes['input_bytes'] = len(original(value['input']))
        return encoded

    provider_module.canonical = measuring
    try:
        try:
            await provider.next_turn(messages, definitions(), {}, dict(
                request_timeout=60, max_input_bytes=48000, max_output_tokens=8192,
                max_response_bytes=2097152, tool_choice='none'))
        except Captured:
            sizes['guard'] = 'passed; capture before network'
        except ProviderError as exc:
            sizes['guard'] = exc.code
    finally:
        provider_module.canonical = original
    sizes['summary_present'] = summary
    sizes['conversation_bytes'] = len(canonical(messages))
    return sizes


async def main():
    bridge = BridgeReader(ROOT / 'data/processed/model-case-bridge-v1', BRIDGE_SHA)
    store = FeatureStore(ROOT / 'data/processed/t219-ibm-day-60-20-20-v1')
    scorer = ModelScorer(ROOT / 'data/eval/ibm-day-lightgbm-unweighted-freeze-001/artifacts')
    with tempfile.TemporaryDirectory(prefix='contrib-provider-') as stage:
        knowledge = KnowledgeStore(Path(stage) / 'knowledge.sqlite')
        corpus = knowledge.publish(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
        retrieval = knowledge.save_configuration(json.loads((
            ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
        for suffix in (1500153, 2959955):
            canonical_id = PREFIX + str(suffix)
            binding = bridge.binding(canonical_id)
            context = bridge.resolve(binding['case_id'], binding['snapshot_ref'])
            row = store.get(canonical_id)
            calculation = compute_local_contributions(scorer, row)
            sidecar = build_sidecar(binding, context, calculation, scorer.manifest, row.features)

            class Repo:
                def get(self, attempt_id):
                    return dict(context_revision=context['context_revision'], run_id='inv_'+'a'*32)

            executor = ToolExecutor(Repo(), 'att_'+'a'*32, 'offline', context, knowledge,
                                    corpus, retrieval, bridge, history_bounds=True)
            baseline = await measure(context, tool_results(executor), False)
            proposed = await measure(context, tool_results(executor, sidecar), True)
            compact = await measure(context, tool_results(executor, sidecar, compact_text=True), True)
            print(json.dumps(dict(row=suffix, sidecar_bytes=len(canonical(sidecar)),
                                  baseline=baseline, proposed=proposed, compact=compact), sort_keys=True))


if __name__ == '__main__':
    asyncio.run(main())
