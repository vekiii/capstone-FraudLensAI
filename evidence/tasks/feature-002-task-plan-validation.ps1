# Documentation-only inspection; never imports the application or runs application tests.
# Run from repo root with powershell -NoProfile -ExecutionPolicy Bypass -File evidence/tasks/feature-002-task-plan-validation.ps1
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$taskText = [IO.File]::ReadAllText((Join-Path $repoRoot 'specs/002-data-and-risk-scoring/tasks.md'), [Text.Encoding]::UTF8)
$specText = [IO.File]::ReadAllText((Join-Path $repoRoot 'specs/002-data-and-risk-scoring/spec.md'), [Text.Encoding]::UTF8)
$plannedPaths = @(
    'backend/src/fraudlens/data_contracts.py',
    'backend/src/fraudlens/data_import.py',
    'backend/src/fraudlens/data_store.py',
    'backend/src/fraudlens/evaluation.py',
    'backend/src/fraudlens/explanations.py',
    'backend/src/fraudlens/feature_history.py',
    'backend/src/fraudlens/model_scoring.py',
    'backend/src/fraudlens/pipeline_cli.py',
    'backend/src/fraudlens/rule_scoring.py',
    'backend/tests/contracts/test_data_models.py',
    'backend/tests/contracts/test_data_scoring.py',
    'backend/tests/contracts/test_models.py',
    'backend/tests/integration/test_data_store.py',
    'backend/tests/integration/test_dataset_api.py',
    'backend/tests/integration/test_evaluation_pipeline.py',
    'backend/tests/integration/test_reproduction.py',
    'backend/tests/integration/test_run_publication.py',
    'backend/tests/unit/test_data_identity.py',
    'backend/tests/unit/test_data_import.py',
    'backend/tests/unit/test_evaluation_metrics.py',
    'backend/tests/unit/test_evaluation_protocol.py',
    'backend/tests/unit/test_explanations.py',
    'backend/tests/unit/test_feature_history.py',
    'backend/tests/unit/test_feature_lineage.py',
    'backend/tests/unit/test_model_artifacts.py',
    'backend/tests/unit/test_model_scoring.py',
    'backend/tests/unit/test_model_selection.py',
    'backend/tests/unit/test_review_snapshot.py',
    'backend/tests/unit/test_rule_scoring.py',
    'backend/tests/unit/test_source_inspection.py',
    'data/mappings/ibm_hi_small_v1.json',
    'evals/protocols/feature_002_v1.json',
    'evidence/tasks/feature-002-api-ui.md',
    'evidence/tasks/feature-002-artifacts-explanations.md',
    'evidence/tasks/feature-002-benchmark.md',
    'evidence/tasks/feature-002-contract-review.md',
    'evidence/tasks/feature-002-convergence.md',
    'evidence/tasks/feature-002-explanation-review.md',
    'evidence/tasks/feature-002-feature-rules.md',
    'evidence/tasks/feature-002-implementation.md',
    'evidence/tasks/feature-002-import-identity.md',
    'evidence/tasks/feature-002-model-metrics.md',
    'evidence/tasks/feature-002-peer-reproduction.md',
    'evidence/tasks/feature-002-phase2.md',
    'evidence/tasks/feature-002-protocol.md',
    'evidence/tasks/feature-002-publication.md',
    'evidence/tasks/feature-002-regression.md',
    'evidence/tasks/feature-002-resource-pilot.md',
    'evidence/tasks/feature-002-source-audit.md',
    'frontend/tests/dataset-api.test.ts',
    'frontend/tests/dataset-contracts.test.ts',
    'frontend/tests/dataset-views.test.ts'
)
$issues = [Collections.Generic.List[string]]::new()
$matches = [regex]::Matches($taskText, '(?m)^- \[ \] (T\d{3})(?: (\[P\]))?(?: \[(US[1-5])\])? (SETUP|GATE|RED|GREEN|DOC|EVIDENCE|REVIEW) \u2014 (.+) \(Depends: (.+)\.\)\r?$')
$tasks = @()
$lookup = @{}
foreach ($match in $matches) {
    $task = [pscustomobject]@{
        id=$match.Groups[1].Value; parallel=($match.Groups[2].Value -eq '[P]')
        story=$match.Groups[3].Value; kind=$match.Groups[4].Value; text=$match.Groups[5].Value
        dependencies=@([regex]::Matches($match.Groups[6].Value,'T\d{3}') | ForEach-Object Value)
    }
    if ($lookup.ContainsKey($task.id)) { $issues.Add("Duplicate ID $($task.id)") }
    $lookup[$task.id]=$task
    $tasks += $task
}
if ($tasks.Count -ne 67) { $issues.Add("Expected 67 tasks; found $($tasks.Count)") }
if ([regex]::Matches($taskText,'(?m)^- \[[ xX]\]').Count -ne $tasks.Count) { $issues.Add('Malformed/completed task checkbox') }
for ($i=0; $i -lt $tasks.Count; $i++) {
    $task=$tasks[$i]
    if ($task.id -ne ('T{0:D3}' -f ($i+1))) { $issues.Add("Nonsequential ID $($task.id)") }
    foreach ($dep in $task.dependencies) {
        if (-not $lookup.ContainsKey($dep) -or [int]$dep.Substring(1) -ge [int]$task.id.Substring(1)) { $issues.Add("Unknown/forward dependency $($task.id) -> $dep") }
    }
    $n=[int]$task.id.Substring(1)
    $story=if($n -in 9..16){'US1'}elseif($n -in 17..25){'US2'}elseif($n -in 26..36){'US3'}elseif($n -in 37..42){'US4'}elseif($n -in 43..59){'US5'}else{''}
    if ($task.story -ne $story) { $issues.Add("Story phase mismatch $($task.id)") }
}
function Get-RedAncestors([string]$taskId) {
    foreach ($dep in $lookup[$taskId].dependencies) {
        if ($lookup.ContainsKey($dep)) {
            if ($lookup[$dep].kind -eq 'RED') { $dep }
            Get-RedAncestors $dep
        }
    }
}
$greenObservations=@()
foreach ($task in $tasks | Where-Object kind -eq 'GREEN') {
    $reds=@(Get-RedAncestors $task.id | Sort-Object -Unique)
    if ($reds.Count -eq 0) { $issues.Add("GREEN without prior RED ancestor $($task.id)") }
    $greenObservations += [pscustomobject]@{task=$task.id; earlier_red_ancestors=$reds}
}
$coverage=@()
foreach ($row in [regex]::Matches($taskText,'(?m)^\| ((?:FR|SC)-\d{3}) \| (.+?) \| (.+?) \| (.+)\|\r?$')) {
    $work=@([regex]::Matches($row.Groups[2].Value,'T\d{3}') | ForEach-Object Value)
    $reds=@([regex]::Matches($row.Groups[3].Value,'T\d{3}') | ForEach-Object Value)
    if ($work.Count -eq 0 -or $reds.Count -eq 0) { $issues.Add("Coverage lacks delivery/test tasks $($row.Groups[1].Value)") }
    foreach ($id in @($work)+@($reds)) { if (-not $lookup.ContainsKey($id)) { $issues.Add("Unknown coverage task $id") } }
    foreach ($id in $reds) { if ($lookup.ContainsKey($id) -and $lookup[$id].kind -ne 'RED') { $issues.Add("Coverage test is not RED $id") } }
    $coverage += [pscustomobject]@{requirement=$row.Groups[1].Value; delivery_tasks=$work; red_tasks=$reds}
}
$required=@([regex]::Matches($specText,'\*\*((?:FR|SC)-\d{3})\*\*') | ForEach-Object {$_.Groups[1].Value} | Sort-Object -Unique)
foreach ($req in $required) { if (@($coverage | Where-Object requirement -eq $req).Count -ne 1) { $issues.Add("Missing/duplicate coverage row $req") } }
if ($required.Count -ne 35 -or $coverage.Count -ne 35) { $issues.Add('Expected 26 FR and 9 SC rows') }
$paths=@('.gitignore')
foreach ($task in $tasks) {
    $taskPaths=@([regex]::Matches($task.text,'\x60([^\x60]+)\x60') | ForEach-Object {$_.Groups[1].Value} | Where-Object {$_ -match '/' -and -not $_.StartsWith('/')})
    $paths += $taskPaths
    if ($taskPaths.Count -eq 0 -and $task.text -notmatch '\x60\.gitignore\x60') { $issues.Add("Task has no exact path $($task.id)") }
}
foreach ($row in [regex]::Matches($taskText,'(?m)^\| (?:FR|SC)-\d{3} \|.*\| ([a-z][a-z; -]+) \|\r?$')) {
    $paths += @($row.Groups[1].Value.Split(';') | ForEach-Object {'evidence/tasks/feature-002-'+$_.Trim()+'.md'})
}
$inventory=@()
foreach ($relative in $paths | Sort-Object -Unique) {
    $absolute=[IO.Path]::GetFullPath((Join-Path $repoRoot $relative))
    if (-not $absolute.StartsWith($repoRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { $issues.Add("Path outside repository $relative") }
    $exists=Test-Path -LiteralPath $absolute -PathType Leaf
    $classification=if($exists){'existing'}elseif($plannedPaths -contains $relative){'planned_new'}else{'missing_reference'}
    if ($classification -eq 'missing_reference') { $issues.Add("Undeclared missing path $relative") }
    $inventory += [pscustomobject]@{path=$relative;exists_at_generation=$exists;classification=$classification}
}
$batches=@(@('T009','T010','T011'),@('T018','T019'),@('T037','T039'),@('T043','T044'),@('T053','T055','T057'))
$parallelObservations=@()
foreach ($batch in $batches) {
    $files=@()
    foreach ($id in $batch) {
        $task=$lookup[$id]
        if (-not $task.parallel) { $issues.Add("Parallel task lacks marker $id") }
        $files += @([regex]::Matches($task.text,'\x60((?:backend|frontend)/tests/[^\x60]+)\x60') | ForEach-Object {$_.Groups[1].Value})
        foreach ($dep in $task.dependencies) { if ($batch -contains $dep) { $issues.Add("Within-batch dependency $id -> $dep") } }
    }
    if (@($files | Sort-Object -Unique).Count -ne $files.Count) { $issues.Add('Shared test file in parallel batch') }
    $parallelObservations += [pscustomobject]@{tasks=$batch;test_files=$files}
}
$result=[ordered]@{
    scope='Static documentation inspection only; no application checks, source audit, training or human approval'
    task_count=$tasks.Count
    checked_boxes=[regex]::Matches($taskText,'(?m)^- \[[xX]\]').Count
    counts_by_story=@($tasks | Group-Object story | ForEach-Object {[pscustomobject]@{story=$(if($_.Name){$_.Name}else{'setup/foundation/final'});count=$_.Count}})
    red_task_count=@($tasks | Where-Object kind -eq 'RED').Count
    green_task_count=@($tasks | Where-Object kind -eq 'GREEN').Count
    parallel_task_count=@($tasks | Where-Object parallel -eq $true).Count
    coverage=$coverage
    green_dependency_observations=$greenObservations
    parallel_batches=$parallelObservations
    file_inventory=$inventory
    existing_path_count=@($inventory | Where-Object classification -eq 'existing').Count
    planned_path_count=@($inventory | Where-Object classification -eq 'planned_new').Count
    issues=@($issues)
    limitations=@('Coverage allocation is not FR/SC satisfaction','RED ancestry does not prove an intended observed failure','Planned code/config/evidence files are absent by design','No Foundation runtime checks run','IBM source/mapping and substantive evaluation pending','Phase 2 compliance unassessed','Consumer/human review and independent reproduction pending')
}
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'feature-002-task-plan-validation.json'),($result | ConvertTo-Json -Depth 12)+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
[pscustomobject]@{tasks=$tasks.Count;requirements=$required.Count;existing_paths=$result.existing_path_count;planned_paths=$result.planned_path_count;document_issues=@($issues);application_checks='not run'} | ConvertTo-Json -Depth 4
if ($issues.Count -gt 0) { exit 1 }

