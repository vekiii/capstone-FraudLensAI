"""Authored-only import/store smoke check; never opens the IBM CSV."""
import csv
import hashlib
import io
import json
import tempfile
from dataclasses import replace
from pathlib import Path

from fraudlens.data_import import (
    HI_SMALL_HEADERS,
    derive_dataset_version,
    iter_canonical_rows,
    parse_canonical_source,
)
from fraudlens.data_store import DatasetStore

ROOT = Path(__file__).resolve().parents[2]


def main():
    mapping = (ROOT / 'data/mappings/ibm_hi_small_v1.json').read_bytes()
    time_digest = bytes.fromhex(json.loads(mapping)['time']['time_policy_sha256'])
    mapping_digest = hashlib.sha256(mapping.replace(b'\r\n', b'\n')).digest()
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(HI_SMALL_HEADERS)
    writer.writerow(['2026/01/01 10:00', 'BANK_A', '0007', 'BANK_B', '0007',
                     '0.000001', 'Euro', '10.20', 'Euro', 'Wire', ''])
    raw = stream.getvalue().encode()
    source_digest = hashlib.sha256(raw).digest()
    version = derive_dataset_version(source_digest, mapping_digest, time_digest)
    parsed = parse_canonical_source(raw, namespace='synthetic:green-smoke',
                                    member='authored.csv')
    assert parsed.report.reconciled()
    assert len(list(iter_canonical_rows(io.BytesIO(raw), namespace='synthetic:green-smoke',
                                        member='authored.csv'))) == 1
    event = parsed.events[0]
    label = parsed.private_labels[0]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'synthetic.sqlite'
        store = DatasetStore(path)
        store.stage(version, source_records=1, source_sha256=source_digest.hex(),
                    mapping_sha256=mapping_digest.hex(),
                    time_policy_sha256=time_digest.hex())
        store.add_event(version, event)
        try:
            store.complete(version)
        except ValueError as exc:
            assert 'Private label' in str(exc)
        else:
            raise AssertionError('Missing private status accepted')
        store.add_private_label(version, label.transaction_id,
                                value=label.value, status=label.status)
        store.complete(version)
        store.activate(version)
        assert store.complete_report(version) == {
            'source_records': 1, 'event_valid': 1, 'event_rejected': 0,
            'label_eligible': 0, 'label_ineligible': 1, 'positives': 0,
            'negatives': 0}
        facts = store.operational_events(version)[0].facts
        assert facts['paid_amount'] == '10.20'
        assert facts['received_amount'] == '0.000001'
        assert 'source_ordinal' not in facts and 'label' not in facts
        store.add_event(version, event)
        try:
            store.add_event(version, replace(event, paid_amount='99.00'))
        except ValueError:
            pass
        else:
            raise AssertionError('Changed complete facts accepted')
        store.close()
        reopened = DatasetStore(path)
        assert reopened.active_version() == version
        assert reopened.operational_events(version)[0].facts == facts
        reopened.close()
    print('synthetic bound import/store/restart smoke: passed')


if __name__ == '__main__':
    main()
