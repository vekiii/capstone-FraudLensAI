# Authorized output/bounds correction, 2026-11-18

User explicitly requests both8192 output-token implementation and code-computed
history-minute bounds. New explicit report_prompt=v6, with old defaultv4 and
historicv5 bytes unchanged. Settings allow max_output_tokens<=8192 only when
explicit OpenAI semanticv8/reportv6 is selected for values>4096. Default remains
4096; application and metered evaluation provider factories derive explicit8192
transport cap from SAVED binding, not mutable settings. Old retries retain old caps.
Request45/selector30/total120,8requests/12tools/input48KB/response2MiB unchanged.
More tokens do not guarantee completion or90s success.

New attempts with reportv6 pin history_bounds_version=1 in binding. ToolExecutor
adds computed window_start_inclusive and window_end_exclusive=floorUTCminute(raw
history cutoff) to public evidence text and exact facts; unavailable history has
null bounds, never guessed zeros. History object/schema and filters unchanged.
Legacy attempts/tool projections omit new fields. New prompt copies computed
values, distinguishes cutoff instant from excluded minute, never computes them.
No old evidence/result/prompt rewriting. New runtime hashes do not inherit old
live acceptance; no paid calls/cycle or .env activation in this implementation.
Tests first: settings/profile gates, SDK wire cap, actual tool evidence and nulls,
worker binding/retry preservation. Existing150/279 counter and failed gate retained.
