# Feature 06 T001 — Zaključani setup i početna regresija

T001 je završen 21. novembra 2026. (Europe/Belgrade) na grani
`006-capstone-evaluation`, HEAD `cbfa969ca34f9d19c72b39a662f3e125e4f373d4`.
Radno stablo je na početku bilo čisto. Sve komande pokrenute su iz
`D:\AIBootcamp\capstone`. [Originalni prompt](../../prompts/development/006-capstone-phase-01.md),
[taskovi](../../specs/006-capstone-evaluation/tasks.md),
[plan](../../specs/006-capstone-evaluation/plan.md) i
[quickstart](../../specs/006-capstone-evaluation/quickstart.md).

Postavljen je `SPECIFY_FEATURE_DIRECTORY=specs/006-capstone-evaluation`.
`powershell -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks`
vratio je exit 0 i očekivanu apsolutnu putanju. Checklist ima 14/14 oznaka.
`.specify/extensions.yml` nije prisutan, pa nema pre/post hookova.

## Instalacija i verzije

Projektni Python 3.14.3 (`uv run --locked python --version`), sistemski
Python 3.14.7 (`py --version`), uv 0.10.9, Node v24.20.0, npm 11.19.0.
Korišćeni su postojeći `uv.lock` revizije 5 i `web/package-lock.json`.

| Komanda | Exit | Ishod |
|---|---:|---|
| `uv sync --locked --group dev` uz `UV_CACHE_DIR=.cache/uv` | 0 | Rezolvirano 50, provereno 49 paketa. |
| `npm.cmd --prefix web ci` u sandboxu | 1 | EACCES pri preuzimanju tldts-core 7.5.4. Pisanje npm loga u korisnički keš takođe nije bilo dostupno. Greška okruženja. |
| `npm.cmd --prefix web ci` sa sandbox eskalacijom | 0 | Dodan 91 paket, audit 92 paketa, npm prijavio 0 ranjivosti. |

## Ciljani backend

Izvršena je ekvivalentna pytest komanda kroz zaključani Python, uz izolovanu
konfiguraciju. Stvarni izlaz je **84 prošla, 0 neuspešnih, exit 0**, za 20.63 s.
Nema failing node ID-jeva. Starlette prijavljuje deprecation upozorenje za
httpx u TestClient-u. Podešavanje transporta i provider SDK pripadaju T003.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY='specs/006-capstone-evaluation'
$env:UV_CACHE_DIR=Join-Path $PWD '.cache/uv'
$run=Join-Path $PWD ('.cache/006-t001-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $run | Out-Null
$env:T001_BASELINE_DIR=$run
@'
import os, sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path.cwd() / 'backend/src'))
from fraudlens.investigation import environment
root = Path(os.environ['T001_BASELINE_DIR'])
environment.ENV_FILE = root / 'absent.env'
for name in list(os.environ):
    if name.startswith(('APP_', 'INVESTIGATION_', 'OPENAI_', 'ANTHROPIC_')):
        del os.environ[name]
def offline(event, args):
    if event == 'socket.connect':
        addr = args[1]
        if not isinstance(addr, tuple) or addr[0] not in ('127.0.0.1', '::1'):
            raise RuntimeError('T001 baseline blocks outbound connections')
sys.addaudithook(offline)
modules='startup cases investigation_api investigation_knowledge_api investigation_recovery_api investigation_review_api'.split()
raise SystemExit(pytest.main([*(f'backend/tests/integration/test_{m}.py' for m in modules), '--basetemp',str(root/'tmp'),'-o',f'cache_dir={root}/cache','--junitxml',str(root/'backend.xml'),'-q','--tb=short']))
'@ | uv run --locked python -
```

JUnit zapis je u ignorisanom direktorijumu
`.cache/006-t001-de4102f2499646149534deadafd5ea15/backend.xml`.
Startup 8, Cases 43, investigation API 9, knowledge 9, recovery 5, review 10.
Koristi se namerno odsutan env fajl, fixture podrazumevani režim i test provider.

## Ciljani React

| Komanda | Exit | Ishod |
|---|---:|---|
| `npm.cmd --prefix web run test -- --run tests/cases-page.test.tsx tests/investigation-knowledge.test.ts tests/investigation-reports.test.ts tests/investigation-recovery.test.ts tests/investigation-review.test.ts` | 0 | 5 modula, 47 prošlih, 0 neuspešnih, 3.66 s. |
| `npm.cmd --prefix web run typecheck` | 0 | `tsc --noEmit`, bez upozorenja. |
| `npm.cmd --prefix web run build` | 0 | Vite 8.3.8, 55 modula, 524 ms. Three.js chunk 742.80 kB prelazi prag upozorenja od 500 kB. |

Web direktorijum nije imao lokalne `.env*` fajlove. RED nije primenljiv na
mehanički setup. Istorijski padovi pune backend regresije ostaju van ovih
ciljanih rezultata. Puni test suite, T098 inspekcija, provider, dataset integracija,
browser i EV evaluacija ostaju za kasnije faze. Ljudski pregled i reprodukcija
drugog člana su na čekanju. [Predaja](feature-006-phase-01-handoff.md).
