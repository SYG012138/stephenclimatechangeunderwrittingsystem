from methodology import assess_taxonomy, credit_screen, illustrative_pricing
from config import TAXONOMY_FRAMEWORKS

def test_official_frameworks_do_not_claim_automatic_alignment():
    for framework, policy in TAXONOMY_FRAMEWORKS.items():
        if policy["mode"] == "manual":
            result = assess_taxonomy(framework, 90, 90, True)
            assert result["aligned"] is None
            assert "manual review" in result["status"].lower()

def test_custom_policy_thresholds_are_explicit():
    framework = "Custom internal policy (configurable thresholds)"
    result = assess_taxonomy(framework, 35, 25, True, 30, 20)
    assert result["aligned"] is True

def test_dscr_screen_is_not_ifrs_stage():
    result = credit_screen(0.8)
    assert "IFRS 9" in result["note"]
    assert "stage" not in result["status"].lower()

def test_pricing_never_claims_market_quote():
    result = illustrative_pricing(True, 1.4, 25)
    assert result["adjustment_bps"] == -15
    assert result["final_margin_bps"] == 235
