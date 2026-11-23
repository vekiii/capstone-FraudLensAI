"""Explicit T058 input-only batch, durable 104 cap; never opens references."""
import asyncio
import copy
import hashlib
import json
import time
from pathlib import Path
from uuid import uuid4

import httpx2

from fraudlens.investigation.context import HistoryReader
from fraudlens.investigation.evaluation import input_only, verify_pack_inputs, verify_seal, write_frozen
from fraudlens.investigation.knowledge import KnowledgeStore
from fraudlens.investigation.models import ROOT, digest
from fraudlens.investigation.provider import OpenAIProvider, ProviderError, compile_report_schema
from fraudlens.investigation.settings import load_settings
from fraudlens.investigation.workflow import InvestigationService

OUT=ROOT/'evals/results/feature-003/live-v1'
OUT.mkdir(parents=True,exist_ok=True)
LEDGER=OUT/'transport-ledger.json'
ledger=json.loads(LEDGER.read_text(encoding='utf-8')) if LEDGER.exists() else dict(limit=104,attempts=[])


class Metered(httpx2.AsyncBaseTransport):
    def __init__(self,identity):
        self.identity=identity
        self.inner=httpx2.AsyncHTTPTransport()

    async def handle_async_request(self,request):
        if len(ledger['attempts'])>=104:
            raise ProviderError('budget_exhausted')
        item=dict(sequence=len(ledger['attempts'])+1,execution=self.identity)
        ledger['attempts'].append(item)
        LEDGER.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
        try:
            response=await self.inner.handle_async_request(request)
            item.update(status=response.status_code,request_id=response.headers.get('x-request-id'))
            return response
        except Exception as exc:
            item['error_type']=type(exc).__name__
            raise
        finally:
            LEDGER.write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')

    async def aclose(self):
        await self.inner.aclose()


async def main():
    protocol=verify_pack_inputs(ROOT/'evals/investigation/protocol.json')
    split=json.loads((ROOT/'evals/investigation/splits.json').read_text(encoding='utf-8'))
    items={x['id']:input_only(x) for x in json.loads((ROOT/'evals/investigation/inputs/investigation.json').read_text(encoding='utf-8'))}
    settings=load_settings()
    assert settings.model.get_secret_value()=='gpt-6-luna'
    settings=settings.model_copy(update=dict(enabled=True,provider='openai',store=OUT/'runs.sqlite'))
    retrieval=verify_seal(json.loads((ROOT/'evals/investigation/freezes/retrieval-v1.json').read_text(encoding='utf-8')))
    knowledge=KnowledgeStore(settings.store)
    corpus=knowledge.publish(ROOT/'data/knowledge/fraudlens-aml-knowledge-v1/manifest.json')
    assert corpus==protocol['corpus_version']
    chosen=retrieval['configurations'][retrieval['deployment']]
    knowledge.save_configuration(chosen)
    freeze=dict(model='gpt-6-luna',runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),capability_record_sha256=hashlib.sha256((ROOT/'evidence/tasks/feature-003-t033-resume-results.json').read_bytes()).hexdigest(),
        settings=settings.model_dump(mode='json'),corpus_version=corpus,retrieval_sha256=digest(chosen),
        compiled_schema_sha256=digest(compile_report_schema()),primary_ids=split['investigation']['held_out'],demo_ids=split['ordinary_live_demo_cases'],
        input_sha256={k:digest(v) for k,v in items.items()},
        code_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in (ROOT/'backend/src/fraudlens/investigation').glob('*.py')},
        prompt_sha256=hashlib.sha256((ROOT/'prompts/application/investigation-v1.md').read_bytes()).hexdigest())
    freeze_path=OUT/'freeze.json'
    if freeze_path.exists():
        assert verify_seal(json.loads(freeze_path.read_text(encoding='utf-8')))==freeze
    else:
        write_frozen(freeze_path,freeze)
    for role,identities in [('primary',split['investigation']['held_out']),('demo',split['ordinary_live_demo_cases'])]:
        for identity in identities:
            target=OUT/(role+'-'+identity+'.json')
            if target.exists():
                continue  # Resume never repeats/cherry-picks a saved primary attempt.
            item=items[identity]
            class Reader:
                def resolve(self,case_id,source_mode,snapshot):
                    assert (case_id,source_mode,snapshot)==tuple(item['context'][k] for k in ('case_id','source_mode','snapshot_ref'))
                    return copy.deepcopy(item['context'])
            def factory(binding):
                return OpenAIProvider(settings.api_key.get_secret_value(),settings.model.get_secret_value(),
                    prompt=binding['prompt']+'\nEvaluation input instruction: '+item['instruction']+'\nProcedure query hints: '+json.dumps(item['procedure_queries']),
                    transport=Metered(role+'-'+identity))
            service=InvestigationService(knowledge.repository,knowledge,settings,factory,HistoryReader(**item['history_fixture']))
            service.context_reader=Reader()
            request={k:item['context'][k] for k in ('case_id','source_mode','snapshot_ref')}
            start=time.perf_counter()
            run=service.create(request,settings.analyst,str(uuid4()))
            result=await service.work_once()
            elapsed=time.perf_counter()-start
            payload=dict(id=identity,role=role,input_sha256=digest(item),freeze_sha256=digest(freeze),
                duration_seconds=elapsed,result=result,evidence=service.evidence(run['attempt_id']),events=service.events(run['attempt_id']))
            write_frozen(target,payload)
            print(json.dumps(dict(id=identity,role=role,state=result['state'],seconds=round(elapsed,3),transport_attempts=len(ledger['attempts']))),flush=True)


if __name__=='__main__':
    asyncio.run(main())
