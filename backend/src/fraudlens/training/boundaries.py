"""Train-fitted, label-separated preparation for scoreable temporal features.

This finite-batch boundary is for synthetic fixtures. Real-source preparation
requires the separate provenance, resource and protocol gates before fitting.
"""

import math
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import numpy as np

from fraudlens.data.features import FEATURE_ORDER

_PARTITIONS = ('train', 'validation', 'test', 'showcase')
_CATEGORIES = ('current_payment_currency', 'current_payment_format')
_DECIMAL_SUMS = (
    'sender_paid_sum_same_currency_24h',
    'receiver_received_sum_same_currency_24h',
)
_UNKNOWN = '__UNKNOWN__'
_NUMERIC = tuple(name for name in FEATURE_ORDER if name not in _CATEGORIES)


@dataclass(frozen=True)
class FeatureView:
    features: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class LabeledView(FeatureView):
    labels: tuple[int, ...]


@dataclass(frozen=True)
class TrainingPreprocessor:
    currency_vocabulary: tuple[str, ...]
    format_vocabulary: tuple[str, ...]

    def transform(self, rows: Iterable[Mapping[str, object]]) -> tuple[dict[str, Any], ...]:
        """Apply frozen vocabularies; never learn categories from these rows."""
        result = []
        for row in rows:
            encoded = {}
            for name in FEATURE_ORDER:
                value = row[name]
                if name in _CATEGORIES:
                    vocabulary = (
                        self.currency_vocabulary if name == _CATEGORIES[0]
                        else self.format_vocabulary
                    )
                    encoded[name] = value if value in vocabulary else _UNKNOWN
                else:
                    encoded[name] = value
            result.append(encoded)
        return tuple(result)

    def matrix(self, features: Iterable[Mapping[str, object]]) -> np.ndarray:
        """Convert exact Decimal sums at the model boundary, then one-hot encode."""
        records = tuple(features)
        width = len(_NUMERIC) + len(self.currency_vocabulary) + len(self.format_vocabulary)
        matrix = np.zeros((len(records), width), dtype=np.float64)
        for row_number, row in enumerate(records):
            for column, name in enumerate(_NUMERIC):
                matrix[row_number, column] = float(row[name])
            for field, vocabulary, offset in (
                (_CATEGORIES[0], self.currency_vocabulary, len(_NUMERIC)),
                (_CATEGORIES[1], self.format_vocabulary,
                 len(_NUMERIC) + len(self.currency_vocabulary)),
            ):
                try:
                    category_index = vocabulary.index(row[field])
                except ValueError:
                    raise ValueError(f'{field} was not transformed by this preprocessor') from None
                matrix[row_number, offset + category_index] = 1.0
        if not np.isfinite(matrix).all():
            raise ValueError('model matrix must contain only finite float64 values')
        return matrix

    @property
    def numeric_width(self) -> int:
        return len(_NUMERIC)


@dataclass(frozen=True)
class TrainingViews:
    preprocessor: TrainingPreprocessor
    train: LabeledView
    validation: LabeledView
    test: FeatureView
    showcase: FeatureView


def _validate_row(row: Mapping[str, object]) -> None:
    if not isinstance(row, Mapping) or set(row) != set(FEATURE_ORDER) | {'transaction_id'}:
        raise ValueError('training input must contain exactly transaction_id and frozen features')
    identity = row['transaction_id']
    if not isinstance(identity, str) or not identity.strip():
        raise ValueError('transaction_id must be nonempty text')
    for name in _CATEGORIES:
        category = row[name]
        if (not isinstance(category, str) or not category.strip()
                or category == _UNKNOWN):
            raise ValueError(f'{name} must be nonempty and cannot use reserved unknown token')
    for name in _NUMERIC:
        value = row[name]
        if name in _DECIMAL_SUMS:
            try:
                number = Decimal(value)
            except (InvalidOperation, TypeError, ValueError):
                raise ValueError(f'{name} must be a finite nonnegative Decimal') from None
            if not number.is_finite() or number < 0:
                raise ValueError(f'{name} must be a finite nonnegative Decimal')
        elif name == 'current_amount_paid_log1p':
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f'{name} must be finite numeric')
            if not math.isfinite(value) or value < 0:
                raise ValueError(f'{name} must be finite nonnegative')
        elif isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f'{name} must be a nonnegative integer')


def _read_labels(
    label_reader: Callable[[str, tuple[str, ...]], Iterable[int]],
    partition: str,
    rows: tuple[Mapping[str, object], ...],
) -> tuple[int, ...]:
    labels = tuple(label_reader(partition, tuple(row['transaction_id'] for row in rows)))
    if len(labels) != len(rows) or any(type(label) is not int or label not in (0, 1)
                                       for label in labels):
        raise ValueError(f'{partition} labels must align with rows and be binary integers')
    return labels


def prepare_training_views(
    rows_by_partition: Mapping[str, Iterable[Mapping[str, object]]],
    *,
    label_reader: Callable[[str, tuple[str, ...]], Iterable[int]],
) -> TrainingViews:
    """Validate every feature row before reading train/validation labels only."""
    if set(rows_by_partition) != set(_PARTITIONS):
        raise ValueError('exact train, validation, test and showcase partitions required')
    rows = {name: tuple(rows_by_partition[name]) for name in _PARTITIONS}
    seen_ids = set()
    for partition in _PARTITIONS:
        if not rows[partition]:
            raise ValueError(f'{partition} must be nonempty')
        for row in rows[partition]:
            _validate_row(row)
            identity = row['transaction_id']
            if identity in seen_ids:
                raise ValueError('transaction_id must be unique across partitions')
            seen_ids.add(identity)
    train = rows['train']
    preprocessor = TrainingPreprocessor(
        currency_vocabulary=tuple(sorted({row[_CATEGORIES[0]] for row in train})) + (_UNKNOWN,),
        format_vocabulary=tuple(sorted({row[_CATEGORIES[1]] for row in train})) + (_UNKNOWN,),
    )
    transformed = {name: preprocessor.transform(rows[name]) for name in _PARTITIONS}
    train_labels = _read_labels(label_reader, 'train', train)
    validation_labels = _read_labels(label_reader, 'validation', rows['validation'])
    return TrainingViews(
        preprocessor=preprocessor,
        train=LabeledView(transformed['train'], train_labels),
        validation=LabeledView(transformed['validation'], validation_labels),
        test=FeatureView(transformed['test']),
        showcase=FeatureView(transformed['showcase']),
    )
