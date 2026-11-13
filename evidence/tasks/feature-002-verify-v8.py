"""User-authorized single-member v8 verification; no credentials or project installs."""
import hashlib
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEMBER = 'HI-Small_Trans.csv'
SLUG = 'ealtman2019/ibm-transactions-for-anti-money-laundering-aml'
ENDPOINT = f'https://www.kaggle.com/api/v1/datasets/download/{SLUG}/{MEMBER}?datasetVersionNumber=8'
DESTINATION = ROOT / 'data/raw/release-verification/v8-20261113-approved'
ORIGINAL = ROOT / 'data/raw' / MEMBER
EVIDENCE = Path(__file__).with_suffix('.json')


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            result.update(chunk)
    return result.hexdigest()


def main():
    assert DESTINATION.resolve().is_relative_to((ROOT / 'data/raw').resolve())
    subprocess.run(['git', 'check-ignore', '--quiet', str(DESTINATION / 'probe.zip')],
                   cwd=ROOT, check=True)
    before = digest(ORIGINAL)
    if EVIDENCE.exists():
        previous = json.loads(EVIDENCE.read_text(encoding='utf-8'))
        target = ROOT / previous.get('reference_path', 'missing-verification-file')
        if (previous.get('status') == 'verified_v8_equivalent' and target.is_file()
                and before == previous['reference_sha256'] == digest(target)):
            print(json.dumps({'status': 'verified_existing_reference_without_redownload',
                              'sha256': before}), flush=True)
            return 0
        print('Existing verification evidence preserved; inspect it before another attempt.', flush=True)
        return 2
    result = dict(requested_version=8, requested_member=MEMBER, endpoint=ENDPOINT,
                  original_sha256_before=before, started_at_utc=datetime.now(timezone.utc).isoformat())
    try:
        request = urllib.request.Request(f'https://www.kaggle.com/api/v1/datasets/view/{SLUG}',
                                         headers={'User-Agent': 'FraudLens-pinned-v8-verification'})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(500000)
            metadata = json.loads(raw)
        result['publisher_metadata'] = {
            key: metadata[key] for key in ['id', 'currentVersionNumber', 'lastUpdated', 'licenseName']}
        result['publisher_metadata_sha256'] = hashlib.sha256(raw).hexdigest()
        if metadata['currentVersionNumber'] != 8:
            raise ValueError('Version-specific license metadata needs separate verification')
        if metadata['licenseName'] != 'Community Data License Agreement - Sharing - Version 1.0':
            raise ValueError('Unexpected publisher license; do not adopt automatically')
        if DESTINATION.exists():
            raise ValueError('Verification directory already exists; preserve it')
        request = urllib.request.Request(ENDPOINT,
                                         headers={'User-Agent': 'FraudLens-pinned-v8-verification'})
        with urllib.request.urlopen(request, timeout=60) as response:
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            result.update(http_status=response.status, content_type=content_type,
                          final_host=urllib.parse.urlsplit(response.geturl()).hostname)
            if content_type not in {'application/zip', 'application/x-zip-compressed',
                                     'application/octet-stream', 'text/csv'}:
                raise ValueError('Non-file response; account/browser access may be required')
            disposition = response.headers.get('Content-Disposition', '')
            if disposition and MEMBER.lower() not in disposition.lower():
                raise ValueError('Unexpected member response; no dataset archive permitted')
            declared_length = response.headers.get('Content-Length')
            if declared_length and int(declared_length) > 600_000_000:
                raise ValueError('Response exceeds single-member verification budget')
            DESTINATION.mkdir(parents=True)
            transfer = DESTINATION / 'HI-Small_Trans.download'
            count = 0
            with transfer.open('xb') as output:
                while block := response.read(1024 * 1024):
                    count += len(block)
                    if count > 600_000_000:
                        raise ValueError('Single-member response size exceeded')
                    output.write(block)
                    if count % (32 * 1024 * 1024) == 0:
                        print(f'Verification download: {count} bytes', flush=True)
            if declared_length and count != int(declared_length):
                raise ValueError('Incomplete download')
        result.update(download_bytes=count, download_sha256=digest(transfer))
        target = DESTINATION / MEMBER
        if zipfile.is_zipfile(transfer):
            with zipfile.ZipFile(transfer) as archive:
                entries = archive.infolist()
                if len(entries) != 1 or entries[0].filename != MEMBER or entries[0].is_dir():
                    raise ValueError('Archive is not exactly the authorized member')
                if entries[0].file_size != ORIGINAL.stat().st_size:
                    result['different_member_size'] = entries[0].file_size
                if entries[0].file_size > 600_000_000:
                    raise ValueError('Uncompressed member exceeds verification budget')
                with archive.open(entries[0]) as source, target.open('xb') as output:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
                result['zip_crc32'] = f'{entries[0].CRC:08x}'
            transfer.rename(DESTINATION / (MEMBER + '.zip'))
        else:
            transfer.rename(target)
        result.update(reference_size_bytes=target.stat().st_size,
                      reference_sha256=digest(target), reference_path=target.relative_to(ROOT).as_posix())
        result['status'] = 'verified_v8_equivalent' if result['reference_sha256'] == before else 'source_mismatch'
        result['original_acquisition_history'] = 'unknown; v8 is an adopted reproducible reference'
    except urllib.error.HTTPError as exc:
        result.update(status='pending_download_access', http_status=exc.code)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        # Do not echo exceptions that may contain redirect URLs, tokens or private paths.
        result.update(status='verification_incomplete', reason_type=type(exc).__name__)
    finally:
        result['original_sha256_after'] = digest(ORIGINAL)
        if result['original_sha256_after'] != before:
            result['status'] = 'original_changed_abort'
        result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        EVIDENCE.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result), flush=True)
    return 0 if result['status'] == 'verified_v8_equivalent' else 2


if __name__ == '__main__':
    raise SystemExit(main())
