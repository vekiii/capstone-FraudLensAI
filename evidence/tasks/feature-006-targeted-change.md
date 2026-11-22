# Feature 06 · T015 · Ciljana izmena na osnovu baseline traga

Offline ocena izvršena je po svih 16 zamrznutih redova posle arhiviranja
opažanja. Baseline ima **11 pass, 4 fail, 1 blocked, 0 not_run**.
[Živi baseline](feature-006-baseline-live.md) · [Negativne kontrole](feature-006-baseline-negative.md).

EV-04 `att_bf083aaa75b142db9bd75722f600dc91` završi obe istorije i
pretragu, a četvrta rezervacija stane na 65.253 bajta pri limitu 48.000.
EV-01 ima isti obrazac i 65.240 bajtova. Arhive sadrže po 17 redova istorije
svake strane i iste vrednosti još jednom u spljoštenim listama `facts`.
Na osnovu tačnih baseline arhivskih dokaza, uklanjanje tih duplikata iz
serializovanog EV-04 zahteva uštedelo bi 19.229 bajtova pre dopune prompta.

U OpenAI adapteru za grupisanu dataset istragu duple stavke
`facts` ispod `events.` izostavljaju se iz transportne projekcije kada
isti skup putanja i vrednosti postoji u punom JSON-u `text`. Kratka dopuna
profilskog prompta modelu kaže kako da prepiše pojedinačnu vrednost i njenu
putanju. Brojevi događaja, oznaka skraćenja, zbirni podaci, arhivske
činjenice i lokalna validacija ostaju dostupni. Plafon transporta je 48.000.
[Adapter](../../backend/src/fraudlens/investigation/provider.py) ·
[Prompt](../../prompts/application/report-parallel-history-v1.md).

Nameravani RED je pao u stvarnom adapteru sa `budget_exhausted` pre
`MockTransport` slanja. Susedni slučaj bez grupisanja je prošao. GREEN
je dao 2/2, uključujući slanje oba istorijska dokaza u raspoloživom ulazu,
pun sadržaj događaja i ista zbirna polja. Ciljana backend regresija dala
je 66/66, Ruff exit 0. Maketa ne troši stvarne pozive.

```powershell
$env:SPECIFY_FEATURE_DIRECTORY = 'specs/006-capstone-evaluation'
$env:PYTHONPATH = 'backend/src'
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_investigation_dataset_binding.py -k provider_boundary --basetemp .cache/006-capstone-red --tb=short
.venv/Scripts/python.exe -m pytest -q backend/tests/integration/test_investigation_dataset_binding.py -k provider_boundary --basetemp .cache/006-capstone-green --tb=short
$tests = @(rg --files backend/tests/integration | rg 'test_(investigation_|capstone_negative)')
.venv/Scripts/python.exe -m pytest -q @tests backend/tests/unit/test_capstone_execution.py --basetemp .cache/006-capstone-targeted-regression --tb=short
.venv/Scripts/python.exe -m ruff check backend/src/fraudlens/investigation/provider.py backend/tests/integration/test_investigation_dataset_binding.py evals/capstone/run.py
```

Izmena je na finalnom SHA-u `d8acc2a335d95e2402f586006925949f4d9f7739`.
Finalni EV-01 zahtev od 40.006 i EV-04 zahtev od 46.288 bajtova prošli
su isti limit od 48.000. EV-01 je dobio validiran nacrt sa citiranim
brojevima iz oba istorijska poziva i sačuvanom odlukom. EV-04 je stigao
do validacije i naišao na `citation_set_mismatch`, posle iskorišćene
četvrte rezervacije. Živi upiti i izbor odlomaka varirali su, pa razlika
u ukupnim bajtovima obuhvata i sastav dokaza u ta dva izvršavanja.
[Finalni trag](feature-006-final-live.md) · [Poređenje](feature-006-before-after.md).
