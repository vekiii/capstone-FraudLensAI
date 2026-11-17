# Fresh retrieval v3 — development review packet

Status: Milan accepted the presented18-row development table/references and
authorized continuation on2026-11-17. One bounded development selection executed:
both variants Recall/MRR0.25/0.25,6/6 correct no-answer; SC-002 remains UNMET.
[Actual execution and limits](../../../evidence/tasks/feature-003-t095-development-selection-20261117.md).
No freeze or held-out run. These18 AI-authored development questions cover
en/sr-Latn/sr-Cyrl,4 answerable+2 no-answer
per language, all six existing documents and unsupported topics with lexical
overlap. Acceptance of the fresh authored packet does not claim comparison with
unseen old questions or independent semantic duplicate auditing.

Milan Gavrić (`milangavric2003`) confirmed the plan on2026-11-17 and subsequently
stated that he had not seen the old held-out questions. This is his declaration,
not an independent audit of prior exposure. No new held-out text was shown.

## Šta Milan sada pregleda

Pregled ove razvojne tabele je sada prihvaćen na osnovu Milanove potvrde;
uputstvo ispod ostaje objašnjenje šta pregled obuhvata, bez zahteva da ga ponavlja.

Otvori [razvojna pitanja](inputs/development.json) i
[predložene reference](reference/development.json). To su **razvojni** primeri,
dozvoljeni za pregled i kasnije podešavanje. Završni skup još nije napravljen.
U [čitljivoj tabeli](development-review.md) svako pitanje ima predlog dokumenta i
obrazloženje; izvorne tekstove otvori preko linkova ispod.

Za svaki red proveri: da li je pitanje jasno; da li navedeni odlomci zaista
odgovaraju; da li neki relevantan odlomak nedostaje; da li kod `no_answer` u ovih
šest dokumenata zaista nema traženog odgovora. Posebno razlikuj opštu preporuku od
konkretnog podatka o klijentu ili važećeg pravila Srbije. Ispravi predlog ako nije
dobar — predložena oznaka nije konačan odgovor zato što ju je AI napisao.

Prijavi primedbe po ID-u (npr. V3-D09), ili potvrdi stvarno pregledane redove i
reference. Navedi ime, datum i da li primeri liče na ranije poznata test-pitanja.
Pregled korpusa od ranije i odobrenje plana nisu automatski pregled ovih redova.

| Document | Exact source |
|---|---|
| ibm-guide | [Field limitations](../../../data/knowledge/fraudlens-aml-knowledge-v1/documents/ibm-guide.md) |
| sim-citation | [Narrative](../../../data/knowledge/fraudlens-aml-knowledge-v1/documents/sim-citation.md) |
| sim-missing | [Missingness](../../../data/knowledge/fraudlens-aml-knowledge-v1/documents/sim-missing.md) |
| sim-review | [Review](../../../data/knowledge/fraudlens-aml-knowledge-v1/documents/sim-review.md) |
| us-confidentiality | [Scope](../../../data/knowledge/fraudlens-aml-knowledge-v1/documents/us-confidentiality.md) |
| us-records | [Supporting documentation](../../../data/knowledge/fraudlens-aml-knowledge-v1/documents/us-records.md) |

## Remaining held-out boundary

The implementation context has not authored/read new held-out questions. A
separate author/reviewer must prepare20 truly new questions with16 answerable/
4 no-answer, language counts en6+2, sr-Latn5+1, sr-Cyrl5+1. The author must avoid
the18 development intent families listed in splits.json and all published T095
diagnostic controls. Declare prior exposure/novelty and provide complete passage
sets/rationales in separate private reference files. Do not tune this candidate
using their content. No placeholder questions/answers or fabricated approvals.

`inputs/held-out.json` and `reference/held-out.json` are deliberately **absent**.
`splits.json` has an empty held_out inventory, so complete freeze/execution fails
closed. Populate reviewed metadata only when a real separate pack exists. The
implementer should receive its metadata/hashes rather than its textual answers.
The separate held-out author/status can be completed later in protocol.json;
changes to development version/corpus/glossary/author still invalidate selection.
The complete freeze pins the whole final protocol. Both actual split
review records bind exact input/reference file hashes, author and reviewer.
The review field `exposure` refers to prior exposure to the old evaluation
holdout. It does not deny that an author/reviewer sees the new references while
authoring/reviewing them; that role must remain separate from candidate tuning.

## Separate offline commands

Use the existing .venv; no dependency installation/provider/.env is required.
New module: `fraudlens.investigation.retrieval_fresh_v3`. It does not change the
old CLI/freezes/results or default search configuration. Example commands below
are gated instructions. The exact completed development execution is in the
linked evidence above; do not replay it or reuse its output directory:

```powershell
$env:PYTHONPATH = 'backend/src'
$pack = 'evals/investigation/retrieval-fresh-v3'
# Only after the concrete development reference review is recorded:
.venv/Scripts/python.exe -m fraudlens.investigation.retrieval_fresh_v3 develop --pack $pack --output .cache/retrieval-v3/development
# Only after separate held-out authoring/review and eligible development:
.venv/Scripts/python.exe -m fraudlens.investigation.retrieval_fresh_v3 freeze --pack $pack --development .cache/retrieval-v3/development/selection.json --output .cache/retrieval-v3/freeze.json
# Only after explicit authorization bound to the concrete freeze,40 searches,0 provider calls:
.venv/Scripts/python.exe -m fraudlens.investigation.retrieval_fresh_v3 execute --pack $pack --freeze .cache/retrieval-v3/freeze.json --authorization .cache/retrieval-v3/authorization.json --output .cache/retrieval-v3/acceptance
.venv/Scripts/python.exe -m fraudlens.investigation.retrieval_fresh_v3 join --pack $pack --freeze .cache/retrieval-v3/freeze.json --predictions .cache/retrieval-v3/acceptance/predictions.json --output .cache/retrieval-v3/metrics.json
```

Reviews are trusted local records, not digital signatures/authentication.
Normalization uses LF hashes. All result files use exclusive creation and sealed
payload digests. Selection/source/corpus/config/file hashes bind the freeze;
execution claims the selection once even if the freeze is copied. An interrupted
claim stays consumed. Do not delete it to rerun. Private references are not opened
during prediction, even for hashing; frozen reference hashes are checked at the
offline join. All prediction rows and errors stay in denominators; errors never
earn correct-no-match credit. Report both variants, language groups, individual
comparisons and fixed0.80/0.70/4-of-4 targets. A synthetic test PASS is not SC-002.
