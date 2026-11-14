"""Controlled RED/GREEN checks for the predeclared validation queue rule."""

from decimal import Decimal
from fractions import Fraction

from backend.tests import validation_ranking_diagnostic as diagnostic


def test_ratio_requires_three_prior_same_currency_rows_and_positive_sum():
    base = {'current_paid_amount': '1.2',
            'sender_paid_count_same_currency_24h': 3,
            'sender_paid_sum_same_currency_24h': '0.9'}
    assert diagnostic._ratio(base) == Fraction(4, 1)
    assert diagnostic._ratio({**base, 'sender_paid_count_same_currency_24h': 2}) is None
    assert diagnostic._ratio({**base, 'sender_paid_sum_same_currency_24h': '0'}) is None
    assert diagnostic._ratio({**base, 'sender_paid_sum_same_currency_24h': None}) is None


def test_queue_uses_score_then_exact_ratio_availability_then_id():
    ids = ['z', 'a', 'x', 'b', 'q', 'r']
    scores = [0.9, 0.9, 0.8, 0.9, 0.9, 0.9]
    ratios = [Fraction(2), None, Fraction(999), Fraction(3),
              Fraction(2), Fraction(Decimal('2.00000000000000000001'))]
    order = diagnostic._queue_order(ids, scores, ratios)
    assert [ids[i] for i in order] == ['b', 'r', 'q', 'z', 'a', 'x']


def test_same_score_unavailable_ratios_use_id_and_old_order_is_preserved():
    ids = ['z', 'a', 'b']
    scores = [0.5, 0.5, 0.5]
    assert diagnostic._queue_order(ids, scores, [None] * 3) == [1, 2, 0]


def test_raw_input_order_does_not_change_selected_id_order():
    ids = ['z', 'b', 'a', 'x']
    scores = [0.7, 0.7, 0.7, 0.9]
    ratios = [Fraction(2), Fraction(3), Fraction(3), None]
    expected = [ids[i] for i in diagnostic._queue_order(ids, scores, ratios)]
    reverse_ids = ids[::-1]
    reverse_scores = scores[::-1]
    reverse_ratios = ratios[::-1]
    actual = [reverse_ids[i] for i in diagnostic._queue_order(
        reverse_ids, reverse_scores, reverse_ratios)]
    assert actual == expected == ['x', 'a', 'b', 'z']
