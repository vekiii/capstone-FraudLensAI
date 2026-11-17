# T095 v3: development questions for human review

AI-authored references accepted by Milan Gavrić/milangavric2003 on2026-11-17
through his presented table/corpus approval. No row-specific objections reported;
no independent comparison against unseen old test questions claimed.
No ranks/scores were used to author these references.
All six document IDs link to their exact source texts in README.md.
Each referenced document has one passage in the unchanged corpus.
Correct/change any row before approving reference hashes.

| ID / language | Question | Proposed complete relevant document set | Rationale |
|---|---|---|---|
| V3-D01 / en | Does a raw transaction timestamp justify inferring the customer's timezone? | ibm-guide | The field guide explicitly forbids inferring timezone from the provided fixture fields. |
| V3-D02 / en | Does a valid citation identifier establish that the analyst interpreted its text faithfully? | sim-citation | The narrative procedure explicitly distinguishes citation identity from faithful interpretation. |
| V3-D03 / en | How should an investigation describe conflicting sources and preserve their versions? | sim-missing | The missingness procedure requires naming conflicting source identities and versions. |
| V3-D04 / en | Does the historical US affiliate guidance grant blanket permission to disclose reports? | us-confidentiality | The historical summary explicitly denies blanket disclosure permission and limits scope to specified US affiliate relationships. |
| V3-D05 / en | What is the mandatory Serbian deadline for filing a suspicious activity report? | no_answer | No current Serbian filing deadline is provided; foreign historical summaries cannot supply it. |
| V3-D06 / en | Which named employee approved this customer's source of funds? | no_answer | The corpus has no customer-specific employee approval records or identities. |
| V3-D07 / sr-Latn | Kako vodič za sintetičke podatke nalaže čuvanje smera iznosa i oznaka valuta? | ibm-guide | The field guide requires preserving directional amount/currency strings. |
| V3-D08 / sr-Latn | Koje izvore treba citirati za činjenice slučaja, a koje za preporučene proceduralne provere? | sim-citation | The narrative procedure distinguishes case-evidence citations for facts from applicable procedure passages for checks. |
| V3-D09 / sr-Latn | Da li nedostupnu istoriju smemo da prikažemo kao praznu istoriju bez ograničenja? | sim-missing | The missingness procedure explicitly forbids replacing unknown history with an empty-history claim. |
| V3-D10 / sr-Latn | Da li istorijske smernice razlikuju prateću dokumentaciju od samog narativa izveštaja? | us-records | The historical records summary distinguishes supporting records from the narrative. |
| V3-D11 / sr-Latn | Koji konkretan API poziv blokira račun nakon eskalacije upozorenja? | no_answer | No account-blocking API or intervention mechanism is documented; the simulated review procedure excludes automatic intervention. |
| V3-D12 / sr-Latn | Koliko godina banka mora da čuva prateću dokumentaciju prema važećem propisu Srbije? | no_answer | The historical excerpt mentions institution-specific procedures without giving a Serbian legal retention period. |
| V3-D13 / sr-Cyrl | Ко доноси одлуку о затварању случаја и да ли је потребно образложење? | sim-review | Closure is an explicit analyst decision requiring a rationale in the simulated review procedure. |
| V3-D14 / sr-Cyrl | Како размотрити алтернативно објашњење без измишљања чињеница о клијенту? | sim-review | The simulated review procedure requires considering alternatives without inventing customer facts. |
| V3-D15 / sr-Cyrl | Да ли је америчка смерница о поверљивости у оквиру повезаних друштава правило Србије? | us-confidentiality | The historical US affiliate summary explicitly states it is not a Serbian rule. |
| V3-D16 / sr-Cyrl | Од чега зависи шта се сматра пратећом документацијом у историјском извору? | us-records | The exact historical excerpt says supporting documentation depends on the facts and circumstances of each filing. |
| V3-D17 / sr-Cyrl | Који је стварни послодавац клијента чији случај истражујемо? | no_answer | No employer or other actual customer identity information exists in this procedural corpus. |
| V3-D18 / sr-Cyrl | Који проценат стварног губитка банке представља износ ове трансакције? | no_answer | The corpus supplies no measured bank-loss percentage for any transaction; the field guide forbids inferring real loss. |
