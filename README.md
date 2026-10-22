# ClimateCredit Underwriting System

An educational decision-support prototype for exploring corporate climate-transition risk, carbon-cost stress, coverage ratios, taxonomy evidence, and illustrative sustainability-linked loan pricing.

> **Important:** This is not a regulated credit model, legal opinion, taxonomy certification, IFRS 9 staging engine, or investment recommendation. Outputs depend on simplified assumptions and user-provided data. Obtain qualified credit, accounting, sustainability and legal review before any real-world use.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run tests with `pytest -q`.

## Model scope and assumptions

- Financial inputs and EBITDA / debt service are in HKD millions; emissions are tonnes of CO2 equivalent; carbon price is USD per tonne.
- FX is an explicit illustrative constant (7.8 HKD/USD), not a live quote.
- Debt service is approximated as total debt times a flat interest rate plus a share of the subject loan as principal repayment. This is not a facility-level amortization schedule.
- The emissions path is linear and ends at the stated five-year reduction target; it is a simplified pathway, not a forecast.
- Negative stressed EBITDA is shown rather than floored away. DSCR/ICR are undefined when the denominator is zero.
- DSCR 1.25x, 250 bps base margin, and -15/+20 bps pricing adjustments are illustrative settings, not universal prudential or market benchmarks.
- Hong Kong and EU taxonomy options require evidence-based manual review. The prototype intentionally does not invent universal pass/fail thresholds. A custom internal policy permits configurable thresholds and is clearly labelled non-regulatory.
- Taxonomy evidence status, credit screening, and IFRS 9 SICR/staging are separate. The app never automatically determines Stage 1 or Stage 2.

## Sample data

Company presets are illustrative examples for demonstration, not verified current financial or emissions disclosures. Confirm all figures against dated primary disclosures before relying on them.

## Preview deployment

No production deployment is performed by this branch. A separate Streamlit Community Cloud preview can be created by deploying this branch as a separate app if the account and repository permissions support it. Do not repoint the existing production app. If preview credentials or deployment permissions are unavailable, use local testing and review the branch instead.
