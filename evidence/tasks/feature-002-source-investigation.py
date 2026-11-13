"""Reproduce T006 public metadata research; no credentials or dataset downloads.

Run from the repository root. Writes only a small sanitized evidence snapshot.
This is an evidence helper, not an importer or source-mapping approval tool.
"""
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'ealtman2019/ibm-transactions-for-anti-money-laundering-aml'
SOURCES = {
    'kaggle_view': f'https://www.kaggle.com/api/v1/datasets/view/{SLUG}',
    'kaggle_files': f'https://www.kaggle.com/api/v1/datasets/list/{SLUG}',
    'ibm_readme': 'https://raw.githubusercontent.com/IBM/AML-Data/'
                  '366436e605ac7713bf4eee8b4fbc45984d64427c/README.md',
    'ibm_formatter': 'https://raw.githubusercontent.com/IBM/Multi-GNN/'
                     '31d5d4578c9f1b9bc89a890a5b344787ee39e6ee/format_kaggle_files.py',
    'kaggle_cli_docs': 'https://raw.githubusercontent.com/Kaggle/kaggle-api/main/docs/datasets.md',
}


def main():
    observations, bodies = {}, {}
    for name, url in SOURCES.items():
        request = urllib.request.Request(url, headers={'User-Agent': 'FraudLens-source-metadata-review'})
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError('Metadata limit exceeded; no partial evidence written')
            observations[name] = {
                'url': url, 'status': response.status,
                'body_sha256': hashlib.sha256(raw).hexdigest(),
                'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
            }
            bodies[name] = raw.decode('utf-8')
    view = json.loads(bodies['kaggle_view'])
    files = json.loads(bodies['kaggle_files'])
    member = next(item for item in files['datasetFiles'] if item['name'] == 'HI-Small_Trans.csv')
    observations['kaggle_view']['selected_metadata'] = {
        name: view[name] for name in ('id', 'title', 'currentVersionNumber', 'lastUpdated', 'licenseName')
    }
    observations['kaggle_view']['published_version_entries'] = [
        {name: item.get(name) for name in ('versionNumber', 'creationDate', 'versionNotes', 'status')}
        for item in view.get('versions', [])
    ]
    observations['kaggle_view']['description_mentions_post_primary_period_laundering'] = (
        'after the specified date period' in view.get('description', '')
        and 'all laundering' in view.get('description', ''))
    observations['kaggle_files']['listed_member_count'] = len(files['datasetFiles'])
    observations['kaggle_files']['selected_member'] = {
        name: member.get(name) for name in ('name', 'totalBytes', 'creationDate')
    }
    observations['kaggle_files']['member_metadata_keys'] = sorted(member)
    observations['ibm_readme']['explicit_data_license_identifier'] = (
        'CDLA-Sharing-1.0' if 'actual data is released under the [CDLA-Sharing-1.0 license]'
        in bodies['ibm_readme'] else None)
    formatter = bodies['ibm_formatter'].splitlines()
    # Only short source-location facts; do not reproduce the upstream implementation.
    observations['ibm_formatter']['relevant_line_numbers'] = {
        key: [i + 1 for i, line in enumerate(formatter) if fragment in line]
        for key, fragment in {
            'sender_bank_with_column_2': 'raw[i,"From Bank"] + raw[i,2]',
            'receiver_bank_with_column_4': 'raw[i,"To Bank"] + raw[i,4]',
            'naive_datetime_parse': 'datetime.strptime(',
            'timestamp_conversion': 'datetime_object.timestamp()',
        }.items()
    }
    source = ROOT / 'data/raw/HI-Small_Trans.csv'
    digest = hashlib.sha256()
    with source.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    snapshot = {
        'scope': 'T006-T008 public metadata and source-document investigation only',
        'local_source': {'member': source.name, 'size_bytes': source.stat().st_size,
                         'sha256': digest.hexdigest()},
        'public_evidence': observations,
        'local_release_verification': 'pending; size match is not a byte or acquisition-history match',
        'source_timezone': 'not established by inspected sources',
        'review_status': 'pending_mapping_review / pending_consumer_review',
    }
    output = Path(__file__).with_suffix('.json')
    output.write_text(json.dumps(snapshot, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps(snapshot, ensure_ascii=True))


if __name__ == '__main__':
    main()
