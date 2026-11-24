# T003 — Zaključane runtime zavisnosti, 21. novembar 2026.

**T003 je završen.** Rad iz korena `D:\AIBootcamp\capstone` na
`006-capstone-evaluation` sa početnim HEAD `055fc06561f8b3d45d1a96e4db15a5ba682deefe`.
[Originalni zahtev](../../prompts/development/006-capstone-phase-02.md).

`git show feature03:uv.lock` na `62f099134c57a3129d28f333545a1398f6e812e4`
potvrđuje OpenAI 3.51.0, httpx2 2.16.0 i jsonschema 4.26.0. SDK i direktno
importovani transport deklarisani su u runtime-u sa tim verzijama.
`jsonschema[format]>=4.23,<5` premešten je iz dev grupe u runtime jer ga
koriste Cases i investigation validatori. Dev `httpx` je ostao 0.28.1.

| Komanda | Exit | Rezultat |
|---|---:|---|
| `uv lock` u sandboxu | 1 | PyPI socket odbijen, OS 10013. |
| `uv lock` sa eskalacijom | 0 | Rezolvirano 57 paketa, 7 dodatih lock zapisa. |
| `uv sync --locked --group dev` | 0 | Instalirano šest paketa na Windows-u. |
| `uv lock --check` | 0 | Zaključana rezolucija odgovara deklaraciji. |
| `uv run --locked ruff check backend` | 0 | Sve provere prošle. |

Sesija koristi `SPECIFY_FEATURE_DIRECTORY=specs/006-capstone-evaluation`
i `UV_CACHE_DIR=.cache/uv`. uv 0.10.9 i projektni Python 3.14.3.
Transitivno su dodati httpcore2 2.16.0, httpx2-jsfetch 1.0 (platformski),
jiter 0.19.0, sniffio 1.3.1 i truststore 0.10.5. Ranije zaključane verzije
ostalih paketa ostale su iste. Lock je generisao uv.

## Offline provere

Komanda `uv run --locked python -` sa wrapper-om ispod potvrdila je importe,
RFC3339 format podršku (`rfc3339-validator` 0.1.4) i **84/84 ciljanih testova,
exit 0, 8.54 s**. Pytest je prijavio jedno upozorenje o ranije importovanom
`anyio` modulu pri assertion rewrite-u. Nema failing node ID-jeva.

```python
import os, sys
from pathlib import Path
from importlib.metadata import version
import pytest
sys.path.insert(0, str(Path.cwd() / 'backend/src'))
from fraudlens.investigation import environment
root = Path(os.environ['T003_TEST_ROOT'])
environment.ENV_FILE = root / 'absent.env'
for key in list(os.environ):
    if key.startswith(('APP_', 'INVESTIGATION_', 'OPENAI_', 'ANTHROPIC_')):
        del os.environ[key]
def offline(event, args):
    if event == 'socket.connect' and (
        not isinstance(args[1], tuple) or args[1][0] not in ('127.0.0.1', '::1')
    ):
        raise RuntimeError('Offline T003')
sys.addaudithook(offline)
import openai, httpx2, jsonschema
from fraudlens.investigation import provider, models, validation
assert jsonschema.FormatChecker().conforms('2026-11-21T12:00:00Z', 'date-time')
assert not jsonschema.FormatChecker().conforms('2026-02-30T12:00:00Z', 'date-time')
print(sys.version.split()[0], {p: version(p) for p in [
    'openai', 'httpx2', 'jsonschema', 'rfc3339-validator', 'httpx']}, flush=True)
modules = 'startup cases investigation_api investigation_knowledge_api investigation_recovery_api investigation_review_api'.split()
raise SystemExit(pytest.main([
    *(f'backend/tests/integration/test_{m}.py' for m in modules),
    '--basetemp', str(root / 'tmp'), '-o', f'cache_dir={root}/cache',
    '--junitxml', str(root / 'results.xml'), '-q', '--tb=short']))
```

`T003_TEST_ROOT` je bio apsolutni put do prethodno kreiranog
`.cache/006-t003-1d9ec89ac7d4469f905e9804423e2ba4`. Investigation API moduli
vežbaju scripted provider, validaciju drafta i citata, recovery i review.
Posebni provider/validation unit moduli postoje na istorijskom Feature 03
ref-u, ali nisu prisutni u ovom checkout-u. SDK transport je ovde proveren
importom. Ova provera potvrđuje lokalnu instalaciju, a provera modelskog
pristupa i capability pripadaju kasnijoj fazi. RED nije primenljiv na ovaj
setup. Puna regresija, React i ljudski pregled ostaju van ove provere.
