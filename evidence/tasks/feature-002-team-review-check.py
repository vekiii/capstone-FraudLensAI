"""Read-only reproduction of T007 review hashes and synthetic identity vectors."""

import csv
import hashlib
import io
import json
import pathlib
import struct
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAPPING = ROOT / 'data/mappings/ibm_hi_small_v1.json'
REFERENCE = '182d0b290c8819e602fc5d77e8df8e904228b032'


def mapping_digest(raw):
    raw.decode('utf-8', 'strict')
    assert not raw.startswith(b'\xef\xbb\xbf')
    assert b'\r' not in raw.replace(b'\r\n', b'')
    return hashlib.sha256(raw.replace(b'\r\n', b'\n')).digest()


def framed(value):
    raw = value.encode('utf-8')
    return struct.pack('>I', len(raw)) + raw


def source_bytes(headers, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def main():
    old = subprocess.check_output([
        'git', 'show', f'{REFERENCE}:data/mappings/ibm_hi_small_v1.json'
    ], cwd=ROOT)
    final = MAPPING.read_bytes()
    mapping = json.loads(final)
    assert 'approved_mapping_sha256' not in mapping['identity']
    assert mapping['execution_policy']['import_allowed'] is False
    selected_policy = json.dumps(mapping['time']['selected_policy'], sort_keys=True,
                                 separators=(',', ':'), ensure_ascii=True).encode('utf-8')
    time = hashlib.sha256(selected_policy).digest()
    assert time.hex() == mapping['time']['time_policy_sha256']

    namespace, member, ordinal = 'synthetic:fraudlens-review:v1', 'review-7.csv', 7
    identity = framed(namespace) + framed(member) + struct.pack('>Q', ordinal)
    transaction = 'D' + hashlib.sha256(b'FraudLensAI/tx/v1\x00' + identity).digest()[:16].hex()
    case = 'C' + hashlib.sha256(b'FraudLensAI/case/v1\x00' + identity).digest()[:16].hex()
    assert transaction == 'D425884d07ae8e842624343aa411210de'
    assert case == 'C1cb19a78e9497dd29eee2de9e7527c60'

    rows = [[f'2022/09/01 12:0{i}', 'BANKA', f'{i:09d}', 'BANKB',
             f'{i+100:09d}', '1.00', 'Euro', '1.00', 'Euro', 'Wire', '0']
            for i in range(1, 7)]
    rows.append(['2022/09/01 12:34', 'BANKA', '000123456', 'BANKB',
                 '000123456', '99.123456', 'Bitcoin', '100.00', 'Euro', 'Wire', ''])
    blank = source_bytes(mapping['csv']['expected_ordered_headers'], rows)
    rows[-1][-1] = '1'
    labeled = source_bytes(mapping['csv']['expected_ordered_headers'], rows)

    def version(source, digest):
        return 'dv_' + hashlib.sha256(
            b'FraudLensAI/dataset-version/v1\x00' +
            hashlib.sha256(source).digest() + digest + time
        ).hexdigest()

    for name, raw, expected in [
        ('reference', old, ('dv_83ce36822c035a5c2ca8e8a8a6c3371e7e3e1371b86df086b83a1c2dbb2b6aa6',
                            'dv_dfa703ee0abc65eee9a19791b23f5c8e3ed0e5d94c3f121b139086259aca984c')),
        ('final', final, ('dv_55e9a2fe16d796aa75aa917f82c516b92caeb7d91fc2f3ee59efc757fca0bb3d',
                        'dv_33e5d9754468adc36e4ceb77a71c4e1e7ab0faad94cd37da29f8e5282b809dfa')),
    ]:
        digest = mapping_digest(raw)
        assert digest == mapping_digest(raw.replace(b'\n', b'\r\n'))
        actual = version(blank, digest), version(labeled, digest)
        assert actual == expected
        print(name, 'raw=', hashlib.sha256(raw).hexdigest(),
              'raw_CRLF=', hashlib.sha256(raw.replace(b'\n', b'\r\n')).hexdigest(),
              'M=', digest.hex(),
              'LF_equals_CRLF=', True, 'dv_blank=', actual[0], 'dv_label1=', actual[1])
    print('D=', transaction, 'C=', case, 'T=', time.hex())
    for path in ('contracts/api.md', 'contracts/data-and-scoring.md',
                 'contracts/schemas.json', 'data-model.md'):
        file = ROOT / 'specs/002-data-and-risk-scoring' / path
        print(path, hashlib.sha256(file.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
