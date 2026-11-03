# Architecture / decision record

**User outcome:** Explain spending change in a way that can be audited instead of relying on natural-language numerical reasoning.

**Design:** CSV data → schema validation → Decimal aggregation → period comparison → rule-constrained explanation → JSON audit record. This design prioritizes correctness over fluency. Structured calculation results are the potential interface to a future LLM.

**Why avoid calling an LLM in v1?** Without a controlled evaluation harness, real transaction connectors and model access, a claim that the system is a production financial AI would be misleading. This portfolio slice first verifies its deterministic accounting substrate.

**Security model:** All inputs are fictional. No customer financial data or credentials. The parser rejects unsupported currencies, duplicate transaction identifiers and malformed money.

**Known caveat:** `amount_eur` tracks *net outflows* by category, not merchant settlement balances. Negative values may represent refunds. This prototype does not handle recurring transfers, pending settlements, multi-currency data, chargebacks, partial months, transaction reclassification or charge reconciliation. In real banking systems, these definitions require product and compliance review.

**Future implementation:** APIs with user authorization and least privilege; encrypted data handling; transaction semantics; independent model evaluator; a structured LLM adapter; prompt-injection and PII-redaction test suites; observability; alerting; human escalation; quality gates and product experimentation. No banking recommendation or automated transaction execution without separate authorization and controls.

**Interview prompts:** (1) Why choose Decimal? (2) What if 5 transactions appear twice? (3) How do you avoid hallucinated balances? (4) How should refunds affect net spend? (5) How does a product team choose reliable metrics? (6) What would make this production ready?