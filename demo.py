"""Usage: python demo.py --csv data/synthetic_transactions.csv --from-month 2026-09 --to-month 2026-10"""
import argparse
import sys
from src.finance_assistant import InputError, run

p = argparse.ArgumentParser(description='Synthetic financial insights assistant')
p.add_argument('--csv', default='data/synthetic_transactions.csv')
p.add_argument('--from-month', default='2026-09')
p.add_argument('--to-month', default='2026-10')
args = p.parse_args()
try:
    print(run(args.csv, args.from_month, args.to_month))
except (InputError, OSError) as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(2)