import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from calculations import run_stress, validate_inputs
from config import (
    USD_HKD, BASE_INTEREST_RATE, ANNUAL_PRINCIPAL_REPAYMENT_SHARE_OF_SUBJECT_LOAN,
    PROJECTION_YEARS, DSCR_SCREENING_LEVEL, BASE_MARGIN_BPS,
    ILLUSTRATIVE_SLL_DISCOUNT_BPS, ILLUSTRATIVE_RISK_PREMIUM_BPS,
    TAXONOMY_FRAMEWORKS,
)
from methodology import assess_taxonomy, credit_screen, illustrative_pricing

st.set_page_config(page_title="ClimateCredit Underwriting System", page_icon="🏦", layout="wide")
st.markdown("""<style>
.stApp { background:#f7f9fc; }
.block-container { padding-top:1.7rem; }
[data-testid="stMetric"] { background:white; border:1px solid #e2e8f0; padding:1rem; border-radius:.7rem; }
.small-note { color:#64748b; font-size:.9rem; }
</style>""", unsafe_allow_html=True)

st.title("🏦 ClimateCredit Underwriting System")
st.caption("Corporate climate-transition risk, scenario analysis and illustrative sustainability-linked loan structuring")
st.warning("Decision-support prototype only — not a regulatory-approved credit model, taxonomy certification, IFRS 9 staging decision, legal opinion or lending recommendation.", icon="⚠️")

COMPANY_DATA = {
    "Custom Input Mode": {"revenue":10000.0,"ebitda":2000.0,"total_debt":5000.0,"loan_amount":1000.0,"emissions":850000.0,"sbti_target_pct":15.0,"green_capex_pct":20.0,"carbon_tax":50.0},
    "Geely Auto (0175.HK) — illustrative": {"revenue":179200.0,"ebitda":14500.0,"total_debt":42000.0,"loan_amount":5000.0,"emissions":1250000.0,"sbti_target_pct":25.0,"green_capex_pct":35.0,"carbon_tax":75.0},
    "Cathay Pacific (0293.HK) — illustrative": {"revenue":94800.0,"ebitda":15100.0,"total_debt":68000.0,"loan_amount":8000.0,"emissions":14200000.0,"sbti_target_pct":12.0,"green_capex_pct":10.0,"carbon_tax":100.0},
    "CR Building Materials (1313.HK) — illustrative": {"revenue":31500.0,"ebitda":4800.0,"total_debt":15000.0,"loan_amount":3000.0,"emissions":28500000.0,"sbti_target_pct":18.0,"green_capex_pct":15.0,"carbon_tax":80.0},
}
with st.sidebar:
    st.header("Underwriting inputs")
    company = st.selectbox("Illustrative borrower case", list(COMPANY_DATA))
    defaults = COMPANY_DATA[company]
    st.caption("Presets are demonstration inputs, not verified current company disclosures.")
    st.subheader("Financials (HKD millions)")
    revenue = st.number_input("Revenue (HKD M)", min_value=0.0, value=defaults["revenue"], step=100.0)
    ebitda = st.number_input("Baseline EBITDA (HKD M)", min_value=0.0, value=defaults["ebitda"], step=50.0)
    total_debt = st.number_input("Total debt (HKD M)", min_value=0.0, value=defaults["total_debt"], step=100.0)
    loan_amount = st.number_input("Subject loan (HKD M)", min_value=0.0, value=defaults["loan_amount"], step=50.0)
    st.subheader("Climate inputs")
    emissions = st.number_input("Scope 1 & 2 emissions (tCO₂e/year)", min_value=0.0, value=defaults["emissions"], step=10000.0)
    sbti_target_pct = st.slider("Five-year emissions reduction target (%)", 0.0, 100.0, float(defaults["sbti_target_pct"]), 1.0)
    green_capex_pct = st.slider("Green CapEx ratio (%)", 0.0, 100.0, float(defaults["green_capex_pct"]), 1.0)
    carbon_tax = st.slider("Carbon price shock (USD/tCO₂e)", 0.0, 500.0, float(defaults["carbon_tax"]), 5.0)
    st.subheader("Model assumptions")
    fx = st.number_input("FX (HKD per USD)", min_value=0.01, value=float(USD_HKD), step=0.1)
    interest_rate_pct = st.number_input("Illustrative interest rate on total debt (%)", min_value=0.0, max_value=100.0, value=BASE_INTEREST_RATE*100, step=0.25)
    principal_share_pct = st.number_input("Annual principal repayment (% of subject loan)", min_value=0.0, max_value=100.0, value=ANNUAL_PRINCIPAL_REPAYMENT_SHARE_OF_SUBJECT_LOAN*100, step=1.0)
    dscr_threshold = st.number_input("Internal DSCR screening level (x)", min_value=0.1, max_value=10.0, value=float(DSCR_SCREENING_LEVEL), step=0.05)
    framework = st.selectbox("Taxonomy framework", list(TAXONOMY_FRAMEWORKS))
    evidence_complete = st.checkbox("Supporting taxonomy evidence assembled")
    if TAXONOMY_FRAMEWORKS[framework]["mode"] == "thresholds":
        st.caption("Internal policy only — not a regulatory taxonomy test.")
        custom_capex_threshold = st.slider("Internal Green CapEx threshold (%)", 0.0, 100.0, 30.0, 1.0)
        custom_target_threshold = st.slider("Internal five-year target threshold (%)", 0.0, 100.0, 20.0, 1.0)
    else:
        custom_capex_threshold, custom_target_threshold = 30.0, 20.0

data = {"revenue":revenue,"ebitda":ebitda,"total_debt":total_debt,"loan_amount":loan_amount,
        "emissions":emissions,"carbon_tax":carbon_tax,"green_capex_pct":green_capex_pct,
        "sbti_target_pct":sbti_target_pct}
errors = validate_inputs(data)
if errors:
    st.error("Please resolve input validation issues:")
    for error in errors:
        st.write(f"- {error}")
    st.stop()
if revenue > 0:
    st.caption(f"Baseline EBITDA margin: {ebitda/revenue:.1%} · Preset: {company}")
else:
    st.info("Revenue is zero; EBITDA margin is not defined.")

tab_overview, tab_scenarios, tab_structuring, tab_feedback = st.tabs([
    "Executive overview", "Stress testing & sensitivity", "Structuring & pricing", "Feedback"
])

tax_assessment = assess_taxonomy(framework, green_capex_pct, sbti_target_pct, evidence_complete,
                                 custom_capex_threshold, custom_target_threshold)
# This demo models a simple straight-line emissions pathway that reaches the stated target at year five.
baseline_rows = run_stress(data, carbon_tax, sbti_target_pct, PROJECTION_YEARS, fx,
                           interest_rate_pct/100, principal_share_pct/100)
baseline_df = pd.DataFrame(baseline_rows)
defined_dscr = [x for x in baseline_df["DSCR (x)"].tolist() if x is not None]
min_dscr = min(defined_dscr) if defined_dscr else None
credit_assessment = credit_screen(min_dscr, dscr_threshold) if min_dscr is not None else {
    "status":"DSCR unavailable", "below_threshold":None,
    "note":"Debt service is zero, so DSCR is undefined. Review the facility assumptions."
}
taxonomy_aligned = tax_assessment["aligned"]
pricing = illustrative_pricing(taxonomy_aligned, min_dscr if min_dscr is not None else -1,
                               sbti_target_pct, BASE_MARGIN_BPS, dscr_threshold,
                               ILLUSTRATIVE_SLL_DISCOUNT_BPS, ILLUSTRATIVE_RISK_PREMIUM_BPS)
interest_impact = loan_amount * pricing["adjustment_bps"] / 10000

with tab_overview:
    st.subheader("Executive summary")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Minimum projected DSCR", f"{min_dscr:.2f}x" if min_dscr is not None else "N/A",
              "Below internal screen" if min_dscr is not None and min_dscr < dscr_threshold else "At/above internal screen" if min_dscr is not None else "Undefined")
    m2.metric("Year 5 emissions", f"{baseline_df.iloc[-1]['Emissions (tCO₂e)']:,.0f} t")
    m3.metric("Year 5 carbon cost", f"HKD {baseline_df.iloc[-1]['Carbon cost (HKD M)']:,.2f} M")
    m4.metric("Illustrative final margin", f"{pricing['final_margin_bps']:.0f} bps")
    st.subheader("Taxonomy evidence review")
    st.write(f"**Selected framework:** {framework}")
    st.write(f"**Screening status:** {tax_assessment['status']}")
    st.write(f"**Green CapEx evidence:** {tax_assessment['capex_test']}")
    st.write(f"**Transition target evidence:** {tax_assessment['target_test']}")
    st.info(tax_assessment["note"])
    if tax_assessment.get("source"):
        st.markdown(f"Framework reference: [{tax_assessment['source']}]({tax_assessment['source']})")
    st.subheader("Credit-risk screen (separate from taxonomy)")
    if min_dscr is not None and min_dscr < dscr_threshold:
        st.error(f"Minimum projected DSCR of {min_dscr:.2f}x is below the selected internal screening level of {dscr_threshold:.2f}x.")
    elif min_dscr is not None:
        st.success(f"Minimum projected DSCR of {min_dscr:.2f}x is at or above the selected internal screening level of {dscr_threshold:.2f}x.")
    else:
        st.warning("DSCR is undefined because the modeled debt-service denominator is zero.")
    st.caption(credit_assessment["note"])
    st.subheader("Five-year base scenario")
    st.dataframe(baseline_df, use_container_width=True, hide_index=True)
    csv = baseline_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download base scenario CSV", csv, file_name="climatecredit_base_scenario.csv", mime="text/csv")
    st.caption("All projections are simplified scenario outputs, not forecasts or lending decisions.")

with tab_scenarios:
    st.subheader("Scenario comparison")
    st.caption("Carbon prices are scaled from the selected input; emissions reduction remains the user-entered five-year target.")
    scenario_defs = [("Base", 1.0), ("Elevated", 1.5), ("Severe", 2.0)]
    all_rows = []
    for label, multiplier in scenario_defs:
        rows = run_stress(data, carbon_tax*multiplier, sbti_target_pct, PROJECTION_YEARS, fx,
                          interest_rate_pct/100, principal_share_pct/100)
        for row in rows:
            all_rows.append({"Scenario":label, **row})
    scenario_df = pd.DataFrame(all_rows)
    summary = scenario_df.groupby("Scenario", sort=False).agg(
        **{"Carbon price (USD/t)":("Carbon cost (HKD M)", lambda x: round(float(x.iloc[0] / (emissions * fx / 1e6), 2), 2) if emissions > 0 and fx > 0 else 0),
           "Minimum DSCR (x)":("DSCR (x)", lambda x: round(min([v for v in x if v is not None]), 2) if any(v is not None for v in x) else None),
           "Year 5 stressed EBITDA (HKD M)":("Stressed EBITDA (HKD M)", "last")}
    ).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)
    chart = px.line(scenario_df, x="Year", y="DSCR (x)", color="Scenario", markers=True,
                    title="Projected DSCR under carbon-price scenarios")
    chart.add_hline(y=dscr_threshold, line_dash="dash", annotation_text="Internal screening level")
    st.plotly_chart(chart, use_container_width=True)
    st.subheader("Sensitivity matrix: carbon price vs. five-year reduction target")
    st.caption("Each cell is the minimum projected DSCR under the selected baseline emissions, facility assumptions, and carbon price / target combination.")
    tax_range = sorted(set([0.0, round(carbon_tax*0.5,2), round(carbon_tax,2), round(carbon_tax*1.5,2), round(carbon_tax*2,2)]))
    target_range = [0, 10, 20, 30, 40, 50, 60]
    matrix = []
    for tax in tax_range:
        row = []
        for target in target_range:
            rows = run_stress(data, tax, target, PROJECTION_YEARS, fx,
                              interest_rate_pct/100, principal_share_pct/100)
            vals = [r["DSCR (x)"] for r in rows if r["DSCR (x)"] is not None]
            row.append(round(min(vals),2) if vals else None)
        matrix.append(row)
    heat_df = pd.DataFrame(matrix, index=[f"{x:g} USD/t" for x in tax_range],
                           columns=[f"{x}%" for x in target_range])
    heat = px.imshow(heat_df, labels={"x":"Five-year emissions reduction target","y":"Carbon price","color":"Minimum DSCR (x)"},
                     aspect="auto", color_continuous_scale="RdYlGn")
    st.plotly_chart(heat, use_container_width=True)

with tab_structuring:
    st.subheader("Illustrative sustainability-linked loan pricing")
    st.caption("The margin rules below are editable demonstration assumptions, not market quotes or calibrated credit policy.")
    p1,p2,p3 = st.columns(3)
    p1.metric("Base margin", f"{pricing['base_margin_bps']:.0f} bps")
    p2.metric("Illustrative adjustment", f"{pricing['adjustment_bps']:+.0f} bps")
    p3.metric("Final margin", f"{pricing['final_margin_bps']:.0f} bps")
    st.write(f"**Rationale:** {pricing['rationale']}")
    st.write(f"**Annual interest impact at the current loan balance:** HKD {interest_impact:,.2f} million (positive = higher cost; negative = lower cost).")
    st.markdown("**Separate the concepts**")
    st.markdown("- Credit-risk pricing should reflect borrower risk, tenor, collateral, seniority, facility terms, and lender policy.")
    st.markdown("- Any sustainability-linked incentive should be tied to documented KPIs/SPTs, verification, reporting, and contractual consequences.")
    st.markdown("- Taxonomy eligibility/alignment is not automatically equivalent to creditworthiness or an SLL performance outcome.")
    with st.expander("Model assumptions and limitations"):
        st.write(f"- FX: {fx:.3f} HKD/USD (user-editable; not live).")
        st.write(f"- Interest: {interest_rate_pct:.2f}% of total debt; principal repayment: {principal_share_pct:.2f}% of subject loan each year.")
        st.write("- Debt service is a simplified proxy, not a contractual amortization schedule.")
        st.write("- Carbon cost = emissions × carbon price × FX ÷ 1,000,000.")
        st.write("- Emissions decline linearly and reach the stated reduction target at the end of year five.")
        st.write("- Negative EBITDA is retained visibly; no artificial floor masks downside.")
        st.write(f"- DSCR threshold ({dscr_threshold:.2f}x), base margin and pricing adjustments are illustrative internal settings.")
        st.write("- IFRS 9 SICR and stage must be assessed using the applicable accounting policy and borrower-specific evidence; this app does not determine them.")
    export = pd.DataFrame([{
        "Borrower preset":company, "Taxonomy framework":framework, "Taxonomy status":tax_assessment["status"],
        "Minimum DSCR (x)":min_dscr, "DSCR screen":credit_assessment["status"],
        "Base margin (bps)":pricing["base_margin_bps"], "Adjustment (bps)":pricing["adjustment_bps"],
        "Final margin (bps)":pricing["final_margin_bps"], "Annual interest impact (HKD M)":interest_impact,
        "FX (HKD/USD)":fx, "Carbon price (USD/t)":carbon_tax,
    }])
    st.download_button("Download underwriting summary CSV", export.to_csv(index=False).encode("utf-8"),
                       file_name="climatecredit_underwriting_summary.csv", mime="text/csv")

with tab_feedback:
    st.subheader("Practitioner feedback")
    st.write("Use this form to record review feedback on model usefulness and assumptions. Submission is not connected to a backend in this prototype.")
    with st.form("feedback_form"):
        role = st.selectbox("Your perspective", ["Credit risk","Relationship manager","Sustainability / ESG","Accounting / finance","Academic / student","Other"])
        usefulness = st.slider("How useful is the prototype?", 1, 5, 3)
        priority = st.selectbox("Highest-priority improvement", ["Better source data","More realistic debt schedules","Taxonomy evidence workflow","IFRS 9 governance","Scenario calibration","Reporting / export","User experience"])
        comments = st.text_area("Comments (optional)")
        submitted = st.form_submit_button("Prepare feedback summary")
    if submitted:
        st.success("Feedback summary prepared below. It has not been transmitted or saved.")
        st.code(f"Perspective: {role}\nUsefulness: {usefulness}/5\nPriority: {priority}\nComments: {comments or 'None'}")

with st.expander("Methodology references and governance notes"):
    st.markdown("- [HKMA — Green and Sustainable Finance](https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/green-and-sustainable-finance/)")
    st.markdown("- [European Commission — EU Taxonomy](https://finance.ec.europa.eu/sustainable-finance/tools-and-standards/eu-taxonomy-sustainable-activities_en)")
    st.markdown("- [IFRS Foundation — IFRS 9 Financial Instruments](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-9-financial-instruments/)")
    st.markdown("- [Loan Market Association — Sustainability-Linked Loan Principles](https://www.lma.eu.com/sustainable-lending/resources)")
    st.caption("Reference links are starting points; check current versions, jurisdictional applicability, and transaction-specific requirements.")
