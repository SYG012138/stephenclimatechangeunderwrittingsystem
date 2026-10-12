import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION & LUXURY STYLING
# ==========================================
st.set_page_config(
    page_title="Stephen ClimateCredit Underwriting System",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global App Background & CJK Font Fallback Support */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, "Microsoft JhengHei", "Microsoft YaHei", "PingFang TC", "PingFang SC", sans-serif;
    }
    
    /* Header Typography */
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.025em;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        font-weight: 400;
        margin-bottom: 1.8rem;
    }
    
    /* Enterprise Card Styling */
    .card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.2rem;
    }
    
    /* Section Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# PRE-LOADED DATA (HKEX COMPANIES)
# ==========================================
COMPANY_DATA = {
    "Custom Input Mode": {
        "revenue": 10000.0,
        "ebitda": 2000.0,
        "total_debt": 5000.0,
        "loan_amount": 1000.0,
        "emissions": 850000.0,
        "sbti_target": 15.0,
        "green_capex": 20.0,
        "carbon_tax": 50.0
    },
    "Geely Auto (0175.HK)": {
        "revenue": 179200.0,
        "ebitda": 14500.0,
        "total_debt": 42000.0,
        "loan_amount": 5000.0,
        "emissions": 1250000.0,
        "sbti_target": 25.0,
        "green_capex": 35.0,
        "carbon_tax": 75.0
    },
    "Cathay Pacific (0293.HK)": {
        "revenue": 94800.0,
        "ebitda": 15100.0,
        "total_debt": 68000.0,
        "loan_amount": 8000.0,
        "emissions": 14200000.0,
        "sbti_target": 12.0,
        "green_capex": 10.0,
        "carbon_tax": 100.0
    },
    "CR Building Materials (1313.HK)": {
        "revenue": 31500.0,
        "ebitda": 4800.0,
        "total_debt": 15000.0,
        "loan_amount": 3000.0,
        "emissions": 28500000.0,
        "sbti_target": 18.0,
        "green_capex": 15.0,
        "carbon_tax": 80.0
    }
}

# ==========================================
# SIDEBAR - CASE SELECTOR & INPUTS
# ==========================================
st.sidebar.markdown("## ⚙️ Control Panel")
selected_company = st.sidebar.selectbox("Select Company Case", list(COMPANY_DATA.keys()))

defaults = COMPANY_DATA[selected_company]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Financial Inputs (HKD M)")
rev_input = st.sidebar.number_input("Revenue", value=defaults["revenue"], step=100.0)
ebitda_input = st.sidebar.number_input("EBITDA", value=defaults["ebitda"], step=50.0)
total_debt_input = st.sidebar.number_input("Total Debt", value=defaults["total_debt"], step=100.0)
loan_amount_input = st.sidebar.number_input("Subject Loan Amount", value=defaults["loan_amount"], step=50.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 Climate & Transition Inputs")
emissions_input = st.sidebar.number_input("Scope 1 & 2 Emissions (tCO2e)", value=defaults["emissions"], step=10000.0)
sbti_input = st.sidebar.slider("SBTi 5-Year Reduction Target (%)", 0.0, 60.0, defaults["sbti_target"], 1.0)
green_capex_input = st.sidebar.slider("Green CapEx Ratio (%)", 0.0, 100.0, defaults["green_capex"], 1.0)
carbon_tax_input = st.sidebar.slider("Carbon Tax Shock Scenario (USD/ton)", 0.0, 200.0, defaults["carbon_tax"], 5.0)

USD_HKD = 7.8

# ==========================================
# MAIN TITLE & OVERVIEW
# ==========================================
st.markdown('<p class="main-header">🏦 Stephen ClimateCredit Underwriting System</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Automated Corporate Transition Credit Assessment, Stress Testing & SLL Pricing under HKMA SPM GS-2 Guidelines</p>', unsafe_allow_html=True)

# ==========================================
# TABS SETUP
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "📈 Risk Assessment & Stress Testing", 
    "💡 Underwriting Structuring & Subsidies", 
    "📝 Practitioner Feedback Survey"
])

# ==========================================
# TAB 1: RISK ASSESSMENT & STRESS TESTING
# ==========================================
with tab1:
    st.markdown("### 1. Phase 2A Taxonomy Alignment Check")
    
    is_capex_aligned = green_capex_input >= 30.0
    is_sbti_aligned = sbti_input >= 20.0
    is_fully_aligned = is_capex_aligned and is_sbti_aligned
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Green CapEx Benchmark", f"{green_capex_input}%", "Target: ≥ 30%", delta_color="normal" if is_capex_aligned else "inverse")
    with col2:
        st.metric("SBTi Target Benchmark", f"{sbti_input}%", "Target: ≥ 20%", delta_color="normal" if is_sbti_aligned else "inverse")
    with col3:
        alignment_status = "🟢 Taxonomy Aligned (Green)" if is_fully_aligned else "🔴 Non-Aligned (Transition/Brown)"
        st.metric("Taxonomy Status", alignment_status)

    with st.expander("📖 View HKMA SPM GS-2 & IFRS 9 Methodology & Regulatory Details"):
        st.markdown("""
        - **HKMA Supervisory Policy Manual (SPM) GS-2**: Focuses on Climate Risk Management, requiring authorized institutions to robustly assess transition risks and carbon tax financial sensitivities.
        - **Phase 2A Taxonomy Alignment**: Requires Green CapEx $\ge 30\%$ and SBTi 5-year reduction target $\ge 20\%$ to qualify as Taxonomy Aligned.
        - **IFRS 9 Staging Trigger**: A Significant Increase in Credit Risk (SICR) forces migration from Stage 1 (12-month ECL) to Stage 2 (Lifetime ECL) if DSCR drops below $1.25\times$ or if the corporate transition plan is non-aligned.
        """)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 2. Forward-Looking 5-Year Stress Testing (Carbon Tax Shock)")
    
    years = [f"Year {i}" for i in range(1, 6)]
    annual_reduction_rate = (sbti_input / 100.0) / 5.0 if is_fully_aligned else 0.01
    
    sim_data = []
    current_emissions = emissions_input
    base_interest_rate = 0.06
    interest_expense = total_debt_input * base_interest_rate
    principal_repayment = loan_amount_input * 0.10
    debt_service = max(interest_expense + principal_repayment, 1.0)
    
    dscr_list = []
    icr_list = []
    
    for i, yr in enumerate(years):
        if i > 0:
            current_emissions *= (1.0 - annual_reduction_rate)
            
        carbon_cost_hkd = (current_emissions * carbon_tax_input * USD_HKD) / 1e6
        stressed_ebitda = max(ebitda_input - carbon_cost_hkd, 10.0)
        
        dscr = stressed_ebitda / debt_service
        icr = stressed_ebitda / max(interest_expense, 1.0)
        
        dscr_list.append(dscr)
        icr_list.append(icr)
        
        sim_data.append({
            "Year": yr,
            "Emissions (tCO2e)": round(current_emissions, 0),
            "Carbon Cost (HKD M)": round(carbon_cost_hkd, 2),
            "Stressed EBITDA (HKD M)": round(stressed_ebitda, 2),
            "DSCR (x)": round(dscr, 2),
            "ICR (x)": round(icr, 2)
        })
        
    df_sim = pd.DataFrame(sim_data)
    st.dataframe(df_sim, use_container_width=True)
    
    min_dscr = min(dscr_list)
    sicr_triggered = (min_dscr < 1.25) or (not is_fully_aligned)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 3. IFRS 9 Staging & SICR Trigger Assessment")
    if sicr_triggered:
        dscr_msg = f"Minimum projected DSCR ({round(min_dscr, 2)}x) is below the 1.25x prudential threshold" if min_dscr < 1.25 else ""
        tax_msg = "Corporate Transition Plan is Non-Aligned with HKMA Phase 2A Taxonomy." if not is_fully_aligned else ""
        connector_msg = " and/or " if (min_dscr < 1.25 and not is_fully_aligned) else ""
        
        st.error(
            f"🚨 **IFRS 9 SICR TRIGGER WARNING: MIGRATION TO STAGE 2 (Lifetime ECL) REQUIRED**\n\n"
            f"Reason: {dscr_msg}{connector_msg}{tax_msg}"
        )
    else:
        st.success(
            "✅ **Credit Risk Standing: STAGE 1 (12-Month ECL)**\n\n"
            "The corporate borrower maintains robust forward-looking debt service coverage (DSCR ≥ 1.25x) and satisfies HKMA Phase 2A Taxonomy alignment criteria."
        )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 4. 5-Year DSCR Trend Visualization")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=dscr_list, mode='lines+markers+text',
        name='Projected DSCR', text=[f"{val:.2f}x" for val in dscr_list],
        textposition="top center", line=dict(color='#0284c7', width=3), marker=dict(size=8)
    ))
    fig.add_hline(
        y=1.25, line_dash="dash", line_color="#dc2626",
        annotation_text="Prudential Threshold (1.25x)", annotation_position="bottom right"
    )
    fig.update_layout(
        xaxis_title="Projection Horizon",
        yaxis_title="Debt Service Coverage Ratio (DSCR)",
        yaxis=dict(range=[0, max(max(dscr_list) + 0.5, 2.0)]),
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 5. Sensitivity Analysis: Carbon Tax vs. Green CapEx Matrix")
    st.markdown("Evaluating minimum projected DSCR across varying carbon tax shocks and green capex commitment levels.")
    
    tax_range = [30, 60, 90, 120, 150]
    capex_range = [10, 20, 30, 40, 50]
    matrix_data = []
    for c_tax in tax_range:
        row = []
        for g_capex in capex_range:
            aligned = g_capex >= 30.0 and sbti_input >= 20.0
            red_rate = (sbti_input / 100.0) / 5.0 if aligned else 0.01
            em = emissions_input
            min_d = 999.0
            for yr_idx in range(5):
                if yr_idx > 0: 
                    em *= (1.0 - red_rate)
                c_cost = (em * c_tax * USD_HKD) / 1e6
                st_ebitda = max(ebitda_input - c_cost, 10.0)
                d = st_ebitda / debt_service
                if d < min_d: 
                    min_d = d
            row.append(round(float(min_d), 2))
        matrix_data.append(row)
        
    df_heat = pd.DataFrame(
        matrix_data,
        index=[f"{t} USD/t" for t in tax_range],
        columns=[f"{x}%" for x in capex_range]
    )
    
    fig_heat = px.imshow(
        df_heat,
        labels=dict(x="Green CapEx Ratio", y="Carbon Tax Scenario", color="Min DSCR (x)"),
        text_auto=True,
        color_continuousscale="RdYlGn"
    )
    fig_heat.update_layout(
        height=340, 
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ==========================================
# TAB 2: UNDERWRITING STRUCTURING & SUBSIDIES
# ==========================================
with tab2:
    st.markdown("### 1. Sustainability-Linked Loan (SLL) Dynamic Pricing Engine")
    
    base_margin_bps = 250.0
    
    if is_fully_aligned and sbti_input >= 25.0:
        pricing_adjustment = -15.0
        pricing_status = "🟢 Transition Incentive Discount Applied (-15 bps)"
    elif not is_fully_aligned or min_dscr < 1.25:
        pricing_adjustment = 20.0
        pricing_status = "🔴 Transition Risk Premium Applied (+20 bps)"
    else:
        pricing_adjustment = 0.0
        pricing_status = "⚪ Standard Pricing (Neutral)"
        
    final_margin_bps = base_margin_bps + pricing_adjustment
    annual_interest_impact = (loan_amount_input * 1e6 * (pricing_adjustment / 10000.0))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4>Pricing Structure Summary</h4>
            <p><b>Base Margin:</b> {base_margin_bps:.0f} bps ({base_margin_bps/100:.2f}%)</p>
            <p><b>Adjustment:</b> {pricing_adjustment:+.0f} bps</p>
            <p><b>Final Loan Margin:</b> <b>{final_margin_bps:.0f} bps ({final_margin_bps/100:.2f}%)</b></p>
            <p style="color: #334155; margin-top: 0.5rem;"><b>Status
