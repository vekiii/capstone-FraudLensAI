"""Verified raw-source hashing and exact-text parsing for IBM HI-Small."""

import csv
import hashlib
import re
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path

EXPECTED_HEADER = (
    'Timestamp',
    'From Bank',
    'Account',
    'To Bank',
    'Account',
    'Amount Received',
    'Receiving Currency',
    'Amount Paid',
    'Payment Currency',
    'Payment Format',
    'Is Laundering',
)

COLUMN_MAP = {
    'timestamp': 0,
    'sender_bank': 1,
    'sender_account': 2,
    'receiver_bank': 3,
    'receiver_account': 4,
    'amount_received': 5,
    'receiving_currency': 6,
    'amount_paid': 7,
    'payment_currency': 8,
    'payment_format': 9,
    'is_laundering': 10,
}


class SourceError(ValueError):
    """Base error for source bytes, schema, and row decoding failures."""


class SourceSchemaError(SourceError):
    """The source header does not match the verified positional schema."""


class SourceRowError(SourceError):
    """A source row cannot be mapped without repairing or losing data."""


def map_ibm_header(header: Sequence[str]) -> dict[str, int]:
    """Require the exact verified header before using duplicate-name positions."""
    if isinstance(header, (str, bytes)):
        raise SourceSchemaError('Source header must be a sequence of field names.')
    actual = tuple(header)
    if actual != EXPECTED_HEADER:
        raise SourceSchemaError('Source header does not match the verified schema.')
    return COLUMN_MAP.copy()


def map_transaction_row(columns: Mapping[str, int], row: Sequence[str]) -> dict[str, str]:
    """Map one parsed CSV row by verified index while retaining every value as text."""
    if dict(columns) != COLUMN_MAP:
        raise SourceSchemaError('Column map does not match the verified schema.')
    if isinstance(row, (str, bytes)) or len(row) != len(EXPECTED_HEADER):
        raise SourceRowError('Source row column count does not match the verified schema.')
    if any(not isinstance(value, str) for value in row):
        raise SourceRowError('Source row values must remain text.')
    return {name: row[index] for name, index in columns.items()}


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Hash original file bytes in bounded memory, without parsing or rewriting them."""
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError('Chunk size must be a positive integer.')
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda: source.read(chunk_size), b''):
            digest.update(chunk)
    return digest.hexdigest()


def stable_transaction_id(source_sha256: str, source_row_number: int) -> str:
    """Build an opaque ID stable for one source hash and its 1-based data row."""
    if not isinstance(source_sha256, str) or re.fullmatch(r'[0-9a-fA-F]{64}', source_sha256) is None:
        raise ValueError('Source identity must be a SHA-256 hex digest.')
    if (
        isinstance(source_row_number, bool)
        or not isinstance(source_row_number, int)
        or source_row_number < 1
    ):
        raise ValueError('Source row number must be a positive integer.')
    return f'ibm-hi-small:{source_sha256.lower()}:row:{source_row_number}'


def iter_source_rows(path: str | Path) -> Iterator[dict[str, str | int]]:
    """Hash first, then stream raw source records with deterministic row identities.

    Timestamps and identifiers remain unmodified text. Timestamp timezone
    interpretation and validation belong to later, source-documented stages.
    """
    source_sha256 = sha256_file(path)
    try:
        with Path(path).open('r', encoding='utf-8', newline='') as source:
            reader = csv.reader(source, strict=True)
            try:
                header = next(reader)
            except StopIteration:
                raise SourceSchemaError('Source CSV is empty and has no header.') from None
            columns = map_ibm_header(header)
            for source_row_number, values in enumerate(reader, start=1):
                mapped = map_transaction_row(columns, values)
                yield {
                    'source_sha256': source_sha256,
                    'source_row_number': source_row_number,
                    'transaction_id': stable_transaction_id(source_sha256, source_row_number),
                    **mapped,
                }
    except UnicodeDecodeError:
        raise SourceError('Source CSV is not valid UTF-8.') from None
    except csv.Error:
        raise SourceError('Source CSV is malformed.') from None
