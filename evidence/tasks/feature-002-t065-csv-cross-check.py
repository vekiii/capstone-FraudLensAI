"""Independent label-free CSV cross-check of five T065 source/history rows."""

import csv
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

SOURCE = Path('data/raw/HI-Small_Trans.csv')
TARGET_ORDINALS = (578886, 2172425, 3635831, 3951325, 4862879)
EXPECTED_ROWS = 5078345
targets = {}
with SOURCE.open(encoding='utf-8', newline='') as stream:
    reader = csv.reader(stream)
    next(reader)
    ordinal = 0
    for ordinal, row in enumerate(reader, 1):
        if ordinal in TARGET_ORDINALS:
            targets[ordinal] = row
    if ordinal != EXPECTED_ROWS or len(targets) != len(TARGET_ORDINALS):
        raise ValueError('Incomplete or unexpected source CSV')

result = {}
for ordinal, row in targets.items():
    t = datetime.strptime(row[0], '%Y/%m/%d %H:%M').replace(tzinfo=timezone.utc)
    result[ordinal] = {'time': t, 'sender': (row[1], row[2]),
                       'currency': row[8], 'count_all': 0,
                       'count_same': 0, 'sum_same': Decimal(0),
                       'facts': {'event_time_utc': t.isoformat(),
                                 'received_amount': row[5],
                                 'received_currency': row[6],
                                 'paid_amount': row[7],
                                 'paid_currency': row[8],
                                 'payment_format': row[9]}}

with SOURCE.open(encoding='utf-8', newline='') as stream:
    reader = csv.reader(stream)
    next(reader)
    ordinal = 0
    for ordinal, row in enumerate(reader, 1):
        for target_ordinal, target in result.items():
            if (ordinal != target_ordinal and (row[1], row[2]) == target['sender']):
                t = datetime.strptime(row[0], '%Y/%m/%d %H:%M').replace(tzinfo=timezone.utc)
                if target['time'] - timedelta(hours=24) <= t < target['time']:
                    target['count_all'] += 1
                    if row[8] == target['currency']:
                        target['count_same'] += 1
                        target['sum_same'] += Decimal(row[7])
    if ordinal != EXPECTED_ROWS:
        raise ValueError('Incomplete second source CSV pass')

for ordinal, target in result.items():
    print(json.dumps({'source_ordinal': ordinal, **target['facts'],
                      'sender_prior_24h_all_currency_count': target['count_all'],
                      'sender_prior_24h_same_currency_count': target['count_same'],
                      'sender_prior_24h_same_currency_paid_sum': str(target['sum_same'])}))
