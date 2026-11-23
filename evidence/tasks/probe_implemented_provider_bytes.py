"""Capture the actual post-join provider request without a network call."""
import asyncio
import json
import tempfile
from pathlib import Path

from probe_contribution_provider_bytes import measure, procedure_result

from fraudlens.bridge_reader import BridgeReader
from fraudlens.investigation.contribution_sidecar import SidecarReader
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.tools import ToolExecutor

ROOT = Path(__file__).resolve().parents[2]
BRIDGE_SHA = '16760ba36a2b36e6f144730c7afae7c855e34b2897166920bc6d185fcf9d2004'
SIDE_SHA = '8edb466a84a186f6115b725d10796c409d1aa5fa065ddfddf0e2e3e1beb12429'
PREFIX = 'ibm-hi-small:b19d39f515523373f991b689c07e11e7b0b95c17a2c27a87d91584ae16c5b040:row:'


async def main():
    bridge = BridgeReader(ROOT / 'data/processed/model-case-bridge-v1', BRIDGE_SHA)
    sidecars = SidecarReader(ROOT / 'data/processed/local-contributions-v1/sidecars.json', SIDE_SHA)
    with tempfile.TemporaryDirectory(prefix='contrib-provider-') as stage:
        knowledge = KnowledgeStore(Path(stage) / 'knowledge.sqlite')
        corpus = knowledge.publish(ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
        retrieval = knowledge.save_configuration(json.loads((
            ROOT / 'data/knowledge/fraudlens-aml-knowledge-v1/retrieval.json').read_text()))
        for suffix in (1500153, 2959955):
            binding = bridge.binding(PREFIX + str(suffix))
            context = bridge.resolve(binding['case_id'], binding['snapshot_ref'])
            sidecar = sidecars.read(binding, context)

            class Repo:
                def get(self, attempt_id):
                    return dict(context_revision=context['context_revision'], run_id='inv_' + 'a' * 32)

            executor = ToolExecutor(Repo(), 'att_' + 'a' * 32, 'offline', context, knowledge,
                                    corpus, retrieval, bridge, history_bounds=True,
                                    local_sidecar=sidecar)
            results = [executor._case()[1], executor._history('sender')[1],
                       executor._history('receiver')[1], procedure_result(executor)]
            measured = await measure(context, results, True, joined_notice=True)
            print(json.dumps(dict(row=suffix, request=measured,
                evidence_items=sum(len(result['evidence']) for result in results),
                all_facts=sum(len(item['facts']) for result in results for item in result['evidence'])),
                sort_keys=True))


if __name__ == '__main__':
    asyncio.run(main())
