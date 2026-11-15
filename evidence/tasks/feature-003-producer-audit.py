"""Read-only Git source reconciliation; never imports producer code or data."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = 'origin/model-implementations'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()


def differences(a, b, path=''):
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            child = path + '/' + key
            result.extend([child] if key not in a or key not in b
                          else differences(a[key], b[key], child))
        return result
    return [] if a == b else [path]


def main():
    commit = git('rev-parse', REF).decode().strip()
    schema_path = 'specs/002-data-and-risk-scoring/contracts/schemas.json'
    current = git('show', f'{commit}:{schema_path}')
    pinned = (ROOT / 'specs/003-ai-investigation/contracts/producer-v2.snapshot.json').read_bytes()
    files = {}
    for name in ('main', 'data_store', 'feature_history', 'data_contracts', 'contracts', 'settings'):
        path = f'backend/src/fraudlens/{name}.py'
        raw = git('show', f'{commit}:{path}')
        tree = ast.parse(raw.decode('utf-8-sig'))
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(dict(name=node.name, line=node.lineno,
                                      arguments=ast.unparse(node.args)))
        files[path] = dict(sha256_lf=sha(raw), functions=functions)
        if name == 'data_contracts':
            files[path]['method_scale_mappings'] = [
                ast.literal_eval(node) for node in ast.walk(tree)
                if isinstance(node, ast.Dict) and any(
                    isinstance(key, ast.Constant) and key.value == 'boosted_sequential_probability'
                    for key in node.keys)]
    result = dict(source_ref=REF, source_commit=commit,
                  scope='Locally available remote-tracking snapshot; no fetch or runtime import',
                  pinned_source_commit='2dd815d85bfc9c2fc70a28baef9c142d551e57e0',
                  pinned_schema_sha256_lf=sha(pinned),
                  current_schema_sha256_lf=sha(current),
                  schema_difference_paths=differences(json.loads(pinned), json.loads(current)),
                  explanation_methods=dict(
                      pinned=json.loads(pinned)['$defs']['ExplanationAvailable']['properties']['method']['enum'],
                      current=json.loads(current)['$defs']['ExplanationAvailable']['properties']['method']['enum']),
                  files=files, human_review='pending', real_producer_execution=False)
    # Do not alter the pinned schema, producer checkout or old evaluation records.
    target = ROOT / 'evidence/tasks/feature-003-producer-audit.json'
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'files'}, indent=2))


if __name__ == '__main__':
    main()
