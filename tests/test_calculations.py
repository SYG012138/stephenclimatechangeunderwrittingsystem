import pytest
from calculations import project_emissions, run_stress, validate_inputs, annual_interest_impact_hkd_m

DATA = {"revenue": 10000, "ebitda": 2000, "total_debt": 5000, "loan_amount": 1000,
        "emissions": 850000, "carbon_tax": 50, "green_capex_pct": 20, "sbti_target_pct": 15}

def test_emissions_pathway_hits_target_at_year_five():
    values = project_emissions(1000, 20)
    assert len(values) == 5
    assert values[0] == pytest.approx(960)
    assert values[-1] == pytest.approx(840)

def test_zero_emissions_has_zero_carbon_cost():
    rows = run_stress({**DATA, "emissions": 0}, 100, 20)
    assert all(row["Carbon cost (HKD M)"] == 0 for row in rows)

def test_negative_stressed_ebitda_is_not_hidden_by_floor():
    rows = run_stress({**DATA, "ebitda": 1}, 200, 0)
    assert rows[0]["Stressed EBITDA (HKD M)"] < 0
    assert rows[0]["EBITDA negative"] is True

def test_invalid_loan_larger_than_debt():
    assert any("exceeds total debt" in e for e in validate_inputs({**DATA, "loan_amount": 6000}))

def test_zero_debt_service_is_explicitly_undefined():
    rows = run_stress({**DATA, "total_debt": 0, "loan_amount": 0}, 0, 0)
    assert rows[0]["DSCR (x)"] is None

def test_bps_interest_impact_units():
    assert annual_interest_impact_hkd_m(1000, 20) == pytest.approx(2)
