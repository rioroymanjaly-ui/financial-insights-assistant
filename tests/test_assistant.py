import csv
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from src.finance_assistant import (InputError, Transaction, parse_transactions,
    month_summary, compare_months, answer_spending_question, money, json_ready)

ROOT = Path(__file__).resolve().parents[1]

def t(id, m, cat, amount):
    return Transaction(id, date.fromisoformat(m), 'demo', cat, Decimal(amount), 'EUR')

class AssistantTests(unittest.TestCase):
    def test_dataset_valid(self):
        self.assertEqual(len(parse_transactions(ROOT/'data/synthetic_transactions.csv')), 13)
    def test_decimal_exactness(self):
        a = [t('1','2026-09-01','Food','0.10'),t('2','2026-09-02','Food','0.20')]
        self.assertEqual(month_summary(a, '2026-09')['net_outflow_eur'], Decimal('0.30'))
    def test_demo_comparison(self):
        r = compare_months(parse_transactions(ROOT/'data/synthetic_transactions.csv'),'2026-09','2026-10')
        self.assertEqual(r['earlier_net_outflow_eur'], Decimal('217.39'))
        self.assertEqual(r['later_net_outflow_eur'], Decimal('332.39'))
        self.assertEqual(r['change_eur'], Decimal('115.00'))
    def test_category_ranking(self):
        r = compare_months(parse_transactions(ROOT/'data/synthetic_transactions.csv'),'2026-09','2026-10')
        self.assertEqual(r['category_changes'][0]['category'], 'Restaurants')
    def test_refunds_net_out(self):
        a = [t('1','2026-09-01','Food','15.00'),t('2','2026-09-02','Food','-5.00')]
        self.assertEqual(month_summary(a, '2026-09')['net_outflow_eur'], Decimal('10.00'))
    def test_no_fake_month_comparison(self):
        with self.assertRaises(InputError):
            compare_months([t('1','2026-09-01','Food','1.00')], '2026-09','2026-10')
    def test_reversed_dates_rejected(self):
        with self.assertRaises(InputError):
            compare_months([t('1','2026-10-01','Food','1.00')], '2026-10','2026-09')
    def test_invalid_month_rejected(self):
        with self.assertRaises(InputError):
            month_summary([], '2026-13')
    def test_duplicates_rejected(self):
        self.assertInvalid(['x,2026-09-01,A,Food,1.00,EUR','x,2026-09-02,A,Food,2.00,EUR'])
    def test_invalid_currency_rejected(self):
        self.assertInvalid(['x,2026-09-01,A,Food,1.00,USD'])
    def test_invalid_float_precision_rejected(self):
        self.assertInvalid(['x,2026-09-01,A,Food,1.009,EUR'])
    def test_nonfinite_rejected(self):
        self.assertInvalid(['x,2026-09-01,A,Food,NaN,EUR'])
    def test_blank_id_rejected(self):
        self.assertInvalid([',2026-09-01,A,Food,1.00,EUR'])
    def test_bad_date_rejected(self):
        self.assertInvalid(['x,2026-09-32,A,Food,1.00,EUR'])
    def test_negative_spending(self):
        x=[t('1','2026-09-01','Food','30.00'),t('2','2026-10-01','Food','20.00')]
        self.assertIn('decreased by €10.00', answer_spending_question(x,'2026-09','2026-10')['answer'])
    def test_no_change(self):
        x=[t('1','2026-09-01','Food','20.00'),t('2','2026-10-01','Food','20.00')]
        self.assertIn('unchanged',answer_spending_question(x,'2026-09','2026-10')['answer'])
    def test_evidence_ids(self):
        x=[t('1','2026-09-01','Food','20.00'),t('2','2026-10-01','Food','30.00')]
        self.assertEqual(answer_spending_question(x,'2026-09','2026-10')['evidence']['source_transaction_ids'], ['1','2'])
    def test_empty_csv(self):
        self.assertInvalid([])
    def test_json_amounts_are_strings(self):
        self.assertEqual(json_ready({'x':Decimal('0.30')}), {'x':'0.30'})
    def test_money_format(self):
        self.assertEqual(money(Decimal('1234.50')),'€1,234.50')
    def assertInvalid(self, rows):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'bad.csv'
            f.write_text('transaction_id,posted_on,merchant,category,amount_eur,currency\n'+'\n'.join(rows),encoding='utf-8')
            with self.assertRaises(InputError):
                parse_transactions(f)

if __name__=='__main__': unittest.main()