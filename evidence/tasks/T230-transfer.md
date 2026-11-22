# T230 snapshot transfer preparation

Prepared the original T210 snapshot files requested for the explicitly authorized T230 test evaluation. The user supplied the frozen prediction SHA-256 `99727d426f78698ee9a0f37ec50c1c900dc848f13bed6ef0756544f76c3f04f7`, threshold `0.2489517623052024`, and explicit authorization to evaluate the frozen predictions without changing model or threshold. No prediction file was present in this workspace; evaluation was not run here.

The source `accepted.jsonl` was read only as bytes for SHA-256 and ZIP creation; its rows and labels were not parsed or displayed. `manifest.json` SHA-256 matched the expected `38e1cdee0e96f73abfc398ff2207c8b8fc1ed0c526a6872e56a1462e55edbb88`. The accepted file SHA-256 matched the manifest value `8a8315288f24a387d1bd0ec3765ac9e64a6b5ce131a634952aee1b302bd9f9ba`.

Created ignored local archive `T230-test-evaluation-snapshot.zip` (240,914,366 bytes) with exactly `t210-hi-small-b19d39f5/accepted.jsonl` and `t210-hi-small-b19d39f5/manifest.json`. ZIP CRC check passed. Archive SHA-256: `c76ab04410a24a150a9e525b23a4f14e980f73394afcc7c2e54ef471705b3ee3`; matching checksum file is `T230-test-evaluation-snapshot.zip.sha256`.

**Pending:** transfer channel/recipient was not specified (request text contains `[navedi konkretan način prenosa koji dogovorite]`), and no messaging or file-transfer connector is available in this session. No transfer occurred. Next step: provide the team's agreed channel or destination, then send the archive and checksum. Showcase labels remain unaccessed.
