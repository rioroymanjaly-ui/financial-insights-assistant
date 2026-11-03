"""Financial insights assistant. Synthetic portfolio demonstration, not a bank product.

Deterministic financial calculations and constrained natural-language explanation.
No LLM or external API is used; an LLM explanation adapter may be added later.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

CENT = Decimal('0.01')
ALLOWED_CURRENCIES = {'EUR'}


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    posted_on: date
    merchant: str
    category: str
    amount: Decimal  # debit is a positive value; refunds/credits are negative
    currency: str


def money(amount: Decimal) -> str:
    return f'€{amount.quantize(CENT, rounding=ROUND_HALF_UP):,.2f}'


def parse_transactions(path: str | Path) -> list[Transaction]:
    result: list[Transaction] = []
    seen = set()
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        required = {'transaction_id', 'posted_on', 'merchant', 'category', 'amount_eur', 'currency'}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise InputError('CSV missing required columns')
        for row_no, row in enumerate(reader, start=2):
            try:
                tid = row['transaction_id'].strip()
                merchant = row['merchant'].strip()
                category = row['category'].strip()
                currency = row['currency'].strip()
                if not tid or not merchant or not category:
                    raise InputError('Blank transaction identifier, merchant, or category')
                if tid in seen:
                    raise InputError(f'Duplicate transaction_id {tid}')
                seen.add(tid)
                if currency not in ALLOWED_CURRENCIES:
                    raise InputError(f'Unsupported currency {currency}; only EUR is supported')
                raw_amount = row['amount_eur'].strip()
                # Decimal rather than float; reject high-precision values and NaN/Infinity.
                if not re.fullmatch(r'-?\d+(?:\.\d{1,2})?', raw_amount):
                    raise InputError(f'Invalid monetary value {raw_amount}')
                amount = Decimal(raw_amount)
                if abs(amount) > Decimal('1000000'):
                    raise InputError('Transaction amount exceeds allowed demo limit')
                posted_on = date.fromisoformat(row['posted_on'].strip())
                result.append(Transaction(tid, posted_on, merchant, category, amount, currency))
            except (KeyError, ValueError, InvalidOperation, TypeError) as e:
                raise InputError(f'Row {row_no}: {e}') from e
    if not result:
        raise InputError('No transactions found')
    return result


def month_summary(transactions: Iterable[Transaction], month: str) -> dict:
    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', month):
        raise InputError('Month must be YYYY-MM')
    category_sums = defaultdict(Decimal)
    count = 0
    for tx in transactions:
        if tx.posted_on.strftime('%Y-%m') == month:
            category_sums[tx.category] += tx.amount
            count += 1
    total = sum(category_sums.values(), Decimal('0'))
    return {'month': month, 'transaction_count': count, 'net_outflow_eur': total,
            'categories': dict(sorted(category_sums.items()))}


def compare_months(transactions: list[Transaction], earlier: str, later: str) -> dict:
    if earlier >= later:
        raise InputError('Earlier month must precede later month')
    prev, curr = month_summary(transactions, earlier), month_summary(transactions, later)
    if prev['transaction_count'] == 0 or curr['transaction_count'] == 0:
        raise InputError('Both months must have transactions; cannot extrapolate missing data')
    total_delta = curr['net_outflow_eur'] - prev['net_outflow_eur']
    categories = []
    for category in sorted(set(prev['categories']) | set(curr['categories'])):
        a = prev['categories'].get(category, Decimal('0'))
        b = curr['categories'].get(category, Decimal('0'))
        categories.append({'category': category, 'earlier_eur': a, 'later_eur': b, 'change_eur': b-a})
    categories.sort(key=lambda c: (-c['change_eur'], c['category']))
    return {'earlier_month': earlier, 'later_month': later,
            'earlier_net_outflow_eur': prev['net_outflow_eur'],
            'later_net_outflow_eur': curr['net_outflow_eur'],
            'change_eur': total_delta, 'category_changes': categories,
            'transaction_count': {'earlier': prev['transaction_count'], 'later': curr['transaction_count']}}


def answer_spending_question(transactions: list[Transaction], earlier: str, later: str) -> dict:
    """Produce a grounded natural-language explanation plus traceable source fields."""
    comparison = compare_months(transactions, earlier, later)
    delta = comparison['change_eur']
    if delta > 0:
        opening = f'Your net spending increased by {money(delta)} from {earlier} to {later}.'
    elif delta < 0:
        opening = f'Your net spending decreased by {money(-delta)} from {earlier} to {later}.'
    else:
        opening = f'Your net spending was unchanged from {earlier} to {later}.'
    changes = [x for x in comparison['category_changes'] if x['change_eur'] > 0]
    contributors = changes[:3]
    if contributors:
        detail = 'Largest category increases: ' + '; '.join(
            f"{x['category']} {money(x['change_eur'])}" for x in contributors) + '.'
    else:
        detail = 'No categories increased in net spending.'
    message = (f'{opening} {detail} Amounts are based only on the provided EUR transactions. '
               'Refunds reduce net spending. This is an informational comparison, not financial advice.')
    return {'answer': message, 'comparison': comparison, 'evidence': {
        'source_transaction_ids': sorted(tx.transaction_id for tx in transactions if tx.posted_on.strftime('%Y-%m') in (earlier, later)),
        'calculation_method': 'SUM(Decimal amount_eur) by month and category; delta = later - earlier',
        'limitations': ['No bank connectivity', 'Only EUR data', 'No inference of fraud or affordability',
                        'Synthetic data; no personalized financial advice']}}


def json_ready(value):
    if isinstance(value, Decimal):
        return format(value.quantize(CENT), '.2f')
    if isinstance(value, dict):
        return {k: json_ready(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_ready(v) for v in value]
    return value


def run(csv_path: str, earlier: str, later: str) -> str:
    return json.dumps(json_ready(answer_spending_question(parse_transactions(csv_path), earlier, later)), indent=2)