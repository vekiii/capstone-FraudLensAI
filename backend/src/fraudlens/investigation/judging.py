"""Offline post-hoc automated evaluation; never imported by runtime tools."""
import copy

from jsonschema import Draft202012Validator

UNIT_SCHEMA = dict(type='object', additionalProperties=False,
    required=['unit_id', 'judgment', 'reason', 'critical_error'], properties=dict(
        unit_id=dict(type='string', minLength=1, maxLength=80),
        judgment=dict(enum=['supported', 'unsupported', 'uncertain', 'applicable', 'present', 'missing']),
        reason=dict(type='string', minLength=1, maxLength=2000), critical_error=dict(type='boolean')))
RATING_SCHEMA = dict(type='object', additionalProperties=False,
    required=['units', 'missingness_correct', 'missingness_reason', 'critical_error', 'additional_issues'],
    properties=dict(units=dict(type='array', items=UNIT_SCHEMA, maxItems=100),
        missingness_correct=dict(type='boolean'),
        missingness_reason=dict(type='string', minLength=1, maxLength=2000),
        critical_error=dict(type='boolean'), additional_issues=dict(type='array', maxItems=50,
            items=dict(type='string', minLength=1, maxLength=2000))))


def validate_rating(packet, value):
    try:
        Draft202012Validator(RATING_SCHEMA).validate(value)
        expected = {u['unit_id']: u for u in packet['units']}
        actual = {u['unit_id']: u for u in value['units']}
        if packet['failed'] or len(actual) != len(value['units']) or set(actual) != set(expected):
            raise ValueError('Unit binding mismatch')
        for identity, unit in actual.items():
            choices = dict(observation={'supported', 'unsupported', 'uncertain'},
                           procedure={'applicable', 'unsupported', 'uncertain'},
                           essential_fact={'present', 'missing', 'uncertain'})
            if unit['judgment'] not in choices[expected[identity]['claim_kind']] or not unit['reason'].strip():
                raise ValueError('Invalid unit judgment')
        if not value['missingness_reason'].strip() or any(not s.strip() for s in value['additional_issues']):
            raise ValueError('Unexplained report judgment')
    except Exception as exc:
        raise ValueError('Invalid automated rating') from exc
    return copy.deepcopy(value)


def aggregate(packets, ratings):
    by_key = {(p['role'], p['scenario_id']): p for p in packets}
    if len(by_key) != len(packets):
        raise ValueError('Duplicate packet')
    expected = {k for k, p in by_key.items() if not p['failed']}
    if set(ratings) != expected:
        raise ValueError('Incomplete or foreign judge outputs')
    clean = {k: validate_rating(by_key[k], v) for k, v in ratings.items()}
    reports, disagreements = [], []
    for (role, identity), packet in by_key.items():
        if role != 'primary':
            continue
        if packet['failed']:
            reports.append(dict(id=identity, failed=True, support_rate=None, essential_coverage=None,
                                passed=False, factual_count=0, essential_count=0))
            continue
        values = [clean[('primary', identity)]]
        if ('secondary', identity) in clean:
            values.append(clean[('secondary', identity)])
        conservative = []
        for unit in packet['units']:
            originals = [next(u for u in v['units'] if u['unit_id'] == unit['unit_id']) for v in values]
            good = {'observation': 'supported', 'procedure': 'applicable',
                    'essential_fact': 'present'}[unit['claim_kind']]
            judgments = [u['judgment'] for u in originals]
            if len(set(judgments)) > 1 or len({u['critical_error'] for u in originals}) > 1:
                disagreements.append(dict(id=identity, unit_id=unit['unit_id'], originals=originals,
                    resolution='unresolved; conservative not-supported/not-present', unresolved=True))
            conservative.append((unit['claim_kind'], all(j == good for j in judgments)))
        factual = [good for kind, good in conservative if kind == 'observation']
        essential = [good for kind, good in conservative if kind == 'essential_fact']
        procedural = [good for kind, good in conservative if kind == 'procedure']
        support = sum(factual) / len(factual) if factual else None
        coverage = sum(essential) / len(essential) if essential else None
        critical = any(v['critical_error'] or any(u['critical_error'] for u in v['units']) for v in values)
        missingness = all(v['missingness_correct'] for v in values)
        additional = [s for v in values for s in v['additional_issues']]
        # Report-level disagreement is preserved as well as per-unit differences.
        if len(values) == 2 and any(values[0][k] != values[1][k]
                                   for k in ('missingness_correct', 'critical_error', 'additional_issues')):
            disagreements.append(dict(id=identity, unit_id=None, originals=values,
                                      resolution='conservative report flags', unresolved=True))
        passed = (support is not None and support >= .9 and coverage is not None and coverage >= .8
                  and not critical and missingness and not additional and all(procedural)
                  and not any(d['id'] == identity for d in disagreements))
        reports.append(dict(id=identity, failed=False, support_rate=support, essential_coverage=coverage,
            passed=passed, critical_error=critical, missingness_correct=missingness,
            additional_issues=additional, factual_count=len(factual), essential_count=len(essential),
            procedural_count=len(procedural), applicable_count=sum(procedural)))
    passing = sum(r['passed'] for r in reports)
    return dict(evaluation_kind='automated_llm_as_judge_post_hoc', human_validation=False,
                report_count=len(reports), failed_reports=sum(r['failed'] for r in reports),
                passing_reports=passing, quality_pass=len(reports) == 8 and passing >= 7
                and not any(r.get('critical_error') for r in reports),
                reports=reports, disagreements=disagreements, original_ratings=copy.deepcopy(ratings_to_list(clean)))


def ratings_to_list(ratings):
    return [dict(role=k[0], scenario_id=k[1], rating=v) for k, v in ratings.items()]
