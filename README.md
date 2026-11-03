# Evidence-grounded Financial Insights Assistant

**Portfolio prototype — not affiliated with Revolut, not a live banking service, not financial advice.**

This is a **deterministic, AI-ready financial operations assistant prototype**, intentionally using synthetic data only. It demonstrates the trust layer that a production LLM-based spending assistant would need: validated inputs, exact Decimal calculations, traceability, reproducible evaluation, and refusal to fabricate missing data. It **does not call an LLM** and does not claim production deployment.

## One-minute demonstration

Requirements: Python 3.10+, no external dependencies.

```bash
python demo.py
python -m unittest discover -s tests -v
```

Expected sample response: September net spend €217.39, October €332.39, increase €115.00, driven by restaurants, groceries and cafes. The JSON contains an evidence trail of source transaction IDs and a machine-readable comparison.

## What problem does it solve?

A user asks, 'Why did my spending increase last month?' A generative model might guess, miscalculate or invent transactions. This implementation forces the response through a deterministic calculations-first pipeline: **validated CSV → currency & precision checks → net-spend aggregation → category deltas → constrained explanation + audit evidence**.

## Example input schema

`transaction_id,posted_on,merchant,category,amount_eur,currency`.
Amounts are debit-positive, credit/refund-negative. Duplicate IDs, mixed currencies, invalid dates, non-finite money values, missing months and malformed inputs are rejected. EU/German-style CSV decimal commas are not supported; this is documented rather than guessed.

## Safeguards and limitations

- No bank credentials or external connectivity, no raw financial data collection, no LLM API calls.
- Exact `decimal.Decimal` arithmetic avoids binary floating-point rounding in currency calculations.
- EUR only, two decimal places, synthetic data only; all claims trace back to transaction IDs.
- Net spending includes refunds. No fraud determination, affordability claim or recommendations about individual investments.
- **Not production ready:** needs identity/authentication, consent, secure storage, encryption, data lifecycle, FX handling, transaction deduplication policy, monitoring, and compliance assessment.
- **No AI model is deployed.** A later LLM integration should accept a structured, validated result object, not raw untrusted user claims, with output validation and an evaluated fallback.

## Product success metrics to test before production

1. Financial calculation exactness: 100% against a controlled labeled fixture set.
2. Unsupported-input handling: 100% rejection of malformed data in negative tests.
3. Grounding: output must cite the original transaction IDs and never claim unsupplied data.
4. Latency: measure p50/p95 after defining a realistic workload.
5. User benefit: task completion and explanation usefulness validated with user research, **not** inferred from tests.

## Relevance to Applied AI engineering

This project is evidence of analytical system design, reliability testing, basic Python product architecture and explicit trade-off decisions. It **does not** establish prior employment in ML engineering, leadership of production teams or experience with PyTorch/TensorFlow.

## Project structure

- `src/finance_assistant.py`: parser, business logic, explanations and JSON serialization.
- `data/synthetic_transactions.csv`: fictional transactions.
- `tests/test_assistant.py`: deterministic unit and negative tests.
- `docs/decision_record.md`: design decisions, next steps and interview talking points.
- `docs/demo_result.json`: generated, inspectable output.
- `docs/test_results.txt`: actual local test run.

## Author / intended use

Independent job-application portfolio evidence. Review and understand the implementation before presenting it as personal engineering work; describe precisely what you built and tested yourself.