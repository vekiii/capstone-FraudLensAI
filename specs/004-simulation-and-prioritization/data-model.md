# Data Model: Simulation Lab and Decision Intelligence

## Frozen scenario

| Entity | Fields and validation |
| --- | --- |
| Scenario reference | `scenario_id`, positive integer `scenario_version` and SHA-256 `content_sha256`. The ID and version identify one immutable revision. Reuse of the pair for changed inputs is a catalog error. |
| Scenario | Reference, title, source, assumptions with stable IDs, horizon `[starts_at, ends_at)`, strictly increasing `window_starts`, defaults and optional generation seed. The first start equals the horizon start. There are 1–12 starts inside the horizon and at most 250 alerts. |
| Score provenance | One source and version per scenario. Include source kind (`fixture`, `rules`, `model`), score kind, scorer version and source data version. A batch source also carries its completed run and dataset references and documented time basis. |
| Alert facts | Unique `alert_id`, `available_at` inside the horizon, finite score in [0,1], positive scenario weight and positive whole estimated review minutes. Include references to the weight and duration assumptions. No outcome fields. |
| Evaluation outcomes | Separate mapping from scenario alert ID to positive or negative. Missing entries are unknown. Reject duplicate or foreign IDs. The outcome mapping is unavailable to ordering and selection. |

All timestamps represent UTC and are compared as instants. Scenario identity covers metadata, configured boundaries, facts and outcomes. Calculate the fingerprint over canonical UTF-8 JSON of the scenario and separate outcome set, excluding the fingerprint itself. Sort object keys and facts/outcomes by ID, preserve ordered windows, emit compact JSON without NaN, and normalize UTC instants and decimal strings before hashing. Assumption references must resolve within the same scenario.

## Comparison recipe

The versioned recipe contains the scenario reference, score threshold, budget in whole minutes per window and the exact version of each of the three strategies. Thresholds use the score's decimal representation. Missing or changed scenario content or strategy versions make the recipe unavailable. Save and reload the recipe locally without introducing server session state or writing case records.

## Replay and result

| Record | Contents |
| --- | --- |
| Window result | Start time, ranked candidate IDs in order, reviewed IDs in selection order and total review minutes used. A reviewed alert leaves the queue permanently for that strategy. |
| Strategy result | Strategy ID, window results, final pending IDs, number reviewed, backlog count, scenario and reviewed unknown-outcome counts, and label-based metrics when at least one label is known. |
| Comparison | Exact recipe, scenario metadata, label-free admitted alert facts for input inspection, and all three strategy results in fixed order. |

Each strategy starts with an independent empty queue and the same inputs. Below-threshold alerts remain outside all queues. Arrivals after the last window start and before the horizon end enter backlog if admitted. Final pending IDs are in availability and ID order.

After selection, count a known positive as found if reviewed. A known positive left unreviewed is missed by threshold or missed in backlog. A reviewed known negative counts as a reviewed negative. Report reviewed and horizon-level unknown counts even when the label-based metrics are unavailable. In a completely empty scenario, report all counts as zero. Surface zero reviewed negatives when that count is known, and unavailable metrics as unavailable.
