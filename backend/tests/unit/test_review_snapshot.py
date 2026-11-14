"""T044: exact latest-100 selection and stable canonical case IDs."""

from datetime import UTC, datetime, timedelta

from backend.tests.phase7_samples import entry


def test_latest_100_tie_order_and_exact_counts():
    from fraudlens.data_store import review_snapshot

    base = datetime(2022, 9, 10, tzinfo=UTC)
    rows = [entry(i, at=base + timedelta(minutes=i // 2))
            for i in range(1, 105)]
    selected = review_snapshot(rows, threshold='0.5')
    assert selected['total_alerts'] == 104
    assert selected['displayed_count'] == 100
    assert selected['truncated'] is True
    ids = [item['transaction_id'] for item in selected['items']]
    assert ids == [f'D{i:032x}' for i in [4, *range(6, 105)]]
    assert selected['selected_time_range']['from'] == rows[3][1]['event_time_utc']
    assert selected['selected_time_range']['to'] == rows[-1][1]['event_time_utc']


def test_no_alert_and_stable_cases_with_large_ids():
    from fraudlens.data_store import review_snapshot

    rows = [entry(1001), entry(1002)]
    empty = review_snapshot(rows, threshold='no_alert')
    assert empty['total_alerts'] == empty['displayed_count'] == 0
    assert empty['selected_time_range'] == {'from': None, 'to': None}
    assert review_snapshot(rows, threshold='0.5')['items'][0]['case_id'] == rows[0][0]
