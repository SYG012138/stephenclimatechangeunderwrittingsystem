"""Pure calculation functions for the illustrative climate-credit model."""
from math import isfinite
from config import USD_HKD, BASE_INTEREST_RATE, ANNUAL_PRINCIPAL_REPAYMENT_SHARE_OF_SUBJECT_LOAN, PROJECTION_YEARS

def validate_inputs(data: dict) -> list[str]:
    errors = []
    nonnegative = ["revenue", "ebitda", "total_debt", "loan_amount", "emissions",
                   "carbon_tax", "green_capex_pct", "sbti_target_pct"]
    for key in nonnegative:
        value = data.get(key)
        if value is None:
            errors.append(f"{key} is required.")
        elif not isinstance(value, (int, float)) or not isfinite(value):
            errors.append(f"{key} must be a finite number.")
        elif value < 0:
            errors.append(f"{key} cannot be negative.")
    if data.get("green_capex_pct", 0) > 100:
        errors.append("green_capex_pct cannot exceed 100%.")
    if data.get("sbti_target_pct", 0) > 100:
        errors.append("sbti_target_pct cannot exceed 100%.")
    if data.get("loan_amount", 0) > data.get("total_debt", 0):
        errors.append("Subject loan amount exceeds total debt; confirm the facility and debt definitions.")
    return errors

def project_emissions(initial_emissions: float, five_year_target_pct: float, years: int = PROJECTION_YEARS) -> list[float]:
    """Linear annual pathway ending exactly at the stated reduction target in year five."""
    if initial_emissions < 0 or not 0 <= five_year_target_pct <= 100 or years < 1:
        raise ValueError("Emissions and target must be non-negative, target <= 100%, and years >= 1.")
    return [initial_emissions * (1 - (five_year_target_pct / 100) * ((year + 1) / years))
            for year in range(years)]

def run_stress(data: dict, carbon_tax_usd_per_ton: float, reduction_target_pct: float,
               years: int = PROJECTION_YEARS, fx_usd_hkd: float = USD_HKD,
               interest_rate: float = BASE_INTEREST_RATE,
               principal_share: float = ANNUAL_PRINCIPAL_REPAYMENT_SHARE_OF_SUBJECT_LOAN) -> list[dict]:
    errors = validate_inputs(data)
    if errors:
        raise ValueError("; ".join(errors))
    if carbon_tax_usd_per_ton < 0 or fx_usd_hkd <= 0 or interest_rate < 0 or principal_share < 0:
        raise ValueError("Tax, interest and principal assumptions must be non-negative; FX must be positive.")
    emissions = project_emissions(data["emissions"], reduction_target_pct, years)
    interest_expense = data["total_debt"] * interest_rate
    principal_repayment = data["loan_amount"] * principal_share
    debt_service = interest_expense + principal_repayment
    results = []
    for i, emitted in enumerate(emissions, start=1):
        carbon_cost = emitted * carbon_tax_usd_per_ton * fx_usd_hkd / 1e6
        stressed_ebitda = data["ebitda"] - carbon_cost  # No artificial EBITDA floor.
        dscr = stressed_ebitda / debt_service if debt_service > 0 else None
        icr = stressed_ebitda / interest_expense if interest_expense > 0 else None
        results.append({
            "Year": f"Year {i}", "Emissions (tCO2e)": round(emitted, 2),
            "Carbon cost (HKD M)": round(carbon_cost, 2),
            "Stressed EBITDA (HKD M)": round(stressed_ebitda, 2),
            "Debt service (HKD M)": round(debt_service, 2),
            "DSCR (x)": round(dscr, 3) if dscr is not None else None,
            "ICR (x)": round(icr, 3) if icr is not None else None,
            "EBITDA negative": stressed_ebitda < 0,
        })
    return results

def annual_interest_impact_hkd_m(loan_amount_hkd_m: float, adjustment_bps: float) -> float:
    return loan_amount_hkd_m * adjustment_bps / 10_000
