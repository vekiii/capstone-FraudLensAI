"""Deliberate future-contract RED; run explicitly, outside application suites."""

from fraudlens.investigation.models import PRODUCER_V2


def test_distinct_local_lightgbm_method_is_admitted():
    methods = PRODUCER_V2['$defs']['ExplanationAvailable']['properties']['method']['enum']
    assert 'lightgbm_pred_contrib_log_odds_v1' in methods
