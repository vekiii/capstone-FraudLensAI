"""T049: public v2 models must agree with the reviewed JSON Schema and semantics."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
from backend.tests.phase7_samples import VERSION, entry
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = json.loads((Path(__file__).resolve().parents[3]
                     / 'specs/002-data-and-risk-scoring/contracts/schemas.json').read_text())


def corpus():
    case, transaction, assessment = entry()
    detail = {'contract_version': 2, 'snapshot_ref': 'run_test_1',
              'dataset_version': VERSION, 'case_id': case,
              'transaction': transaction, 'risk_assessment': assessment}
    item = {'case_id': case, 'transaction_id': transaction['transaction_id'],
            'event_time': transaction['event_time_utc'], 'score': assessment['score'],
            'score_kind': assessment['score_kind'], 'score_source': 'rules'}
    listing = {'contract_version': 2, 'snapshot_ref': 'run_test_1',
               'dataset_version': VERSION, 'data_source': 'ibm_aml_hi_small',
               'score_source': 'rules', 'scorer_version': 'rules-v1',
               'total_alerts': 1, 'displayed_count': 1, 'truncated': False,
               'selected_time_range': {'from': item['event_time'],
                                       'to': item['event_time']}, 'items': [item]}
    health = {'contract_version': 2, 'status': 'ok', 'mode': 'dataset',
              'data_source': 'ibm_aml_hi_small', 'score_source': 'rules',
              'dataset_version': VERSION, 'active_run_id': 'run_test_1'}
    return health, listing, detail


@pytest.mark.parametrize('name,index', [('HealthV2', 0), ('CaseListV2', 1),
                                       ('CaseDetailV2', 2)])
def test_valid_schema_and_model_parity(name, index):
    from fraudlens import data_contracts

    payload = corpus()[index]
    validator = Draft202012Validator(
        {'$schema': SCHEMA['$schema'], '$defs': SCHEMA['$defs'],
         '$ref': f'#/$defs/{name}'}, format_checker=FormatChecker())
    assert validator.is_valid(payload)
    model = getattr(data_contracts, name).model_validate(payload)
    assert model.model_dump(mode='json') == payload


@pytest.mark.parametrize('change', [
    lambda d: d['transaction'].update(label=1),
    lambda d: d['transaction'].update(event_time_utc='2022-02-30T10:00:00Z'),
    lambda d: d['transaction']['paid'].update(amount='1250.000\n'),
    lambda d: d['transaction']['paid'].update(currency='x' * 18),
    lambda d: d['risk_assessment'].update(score=float('nan')),
    lambda d: d['risk_assessment'].update(run_id='run_other'),
    lambda d: d['risk_assessment']['explanation'].update(explained_scale='log_odds'),
    lambda d: d['risk_assessment']['explanation'].update(base_value=0.1),
])
def test_invalid_or_inconsistent_detail_rejected(change):
    from fraudlens.data_contracts import CaseDetailV2

    payload = deepcopy(corpus()[2])
    change(payload)
    with pytest.raises(ValueError):
        CaseDetailV2.model_validate(payload)


def test_list_counts_order_and_source_are_semantic():
    from fraudlens.data_contracts import CaseListV2

    payload = corpus()[1]
    for change in ({'displayed_count': 0}, {'truncated': True},
                   {'score_source': 'model'}, {'snapshot_ref': 'run_other\n'}):
        with pytest.raises(ValueError):
            CaseListV2.model_validate(payload | change)
