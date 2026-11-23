"""Offline-only judge calibration; never a source of runtime case facts."""
from fraudlens.investigation.judging import validate_rating


def assess_calibration(packets, ratings, expectations):
    controls = {p['scenario_id']: p for p in packets if p['role'] == 'calibration'}
    if len(controls) != sum(p['role'] == 'calibration' for p in packets):
        raise ValueError('Duplicate calibration packet')
    expected_ids = [e['scenario_id'] for e in expectations]
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError('Duplicate calibration expectation')
    cases = []
    for expected in expectations:
        identity = expected['scenario_id']
        value = ratings.get(('calibration', identity))
        matched = False
        if identity in controls and value is not None:
            try:
                clean = validate_rating(controls[identity], value)
                units = {u['unit_id']: u for u in clean['units']}
                matched = (set(units) == set(expected['units'])
                    and clean['critical_error'] is expected['critical_error']
                    and clean['missingness_correct'] is expected['missingness_correct']
                    and (not expected['no_additional_issues'] or not clean['additional_issues'])
                    and all(units[key]['judgment'] == wanted['judgment']
                            and units[key]['critical_error'] is wanted['critical_error']
                            for key, wanted in expected['units'].items()))
            except (ValueError, KeyError, TypeError):
                matched = False
        cases.append(dict(scenario_id=identity, matched=matched))
    actual_ids = {identity for role, identity in ratings if role == 'calibration'}
    complete = set(controls) == set(expected_ids) == actual_ids
    return dict(passed=bool(cases) and complete and all(c['matched'] for c in cases), cases=cases)
