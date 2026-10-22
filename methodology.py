"""Policy labels and conservative decision-support rules."""
from config import TAXONOMY_FRAMEWORKS

def assess_taxonomy(framework: str, green_capex_pct: float, sbti_target_pct: float,
                    evidence_complete: bool, custom_capex_threshold: float = 30.0,
                    custom_target_threshold: float = 20.0) -> dict:
    """Return screening status, never a legal/regulatory certification."""
    policy = TAXONOMY_FRAMEWORKS[framework]
    if policy["mode"] == "manual":
        status = "Evidence complete — manual review required" if evidence_complete else "Evidence incomplete — review required"
        return {
            "framework": framework, "status": status, "aligned": None,
            "capex_test": "Not automatically assessed",
            "target_test": "Not automatically assessed",
            "note": policy["description"], "source": policy["source"],
        }
    capex_pass = green_capex_pct >= custom_capex_threshold
    target_pass = sbti_target_pct >= custom_target_threshold
    return {
        "framework": framework,
        "status": "Meets configured internal screen" if capex_pass and target_pass else "Does not meet configured internal screen",
        "aligned": bool(capex_pass and target_pass),
        "capex_test": f"{'Pass' if capex_pass else 'Below threshold'} ({green_capex_pct:.1f}% vs {custom_capex_threshold:.1f}%)",
        "target_test": f"{'Pass' if target_pass else 'Below threshold'} ({sbti_target_pct:.1f}% vs {custom_target_threshold:.1f}%)",
        "note": policy["description"], "source": policy["source"],
    }

def credit_screen(min_dscr: float, dscr_threshold: float = 1.25) -> dict:
    """Internal screening only; does not determine IFRS 9 stage or SICR."""
    return {
        "status": "Below internal DSCR screen" if min_dscr < dscr_threshold else "At/above internal DSCR screen",
        "below_threshold": min_dscr < dscr_threshold,
        "note": "A DSCR screen is one risk indicator, not an IFRS 9 SICR or staging conclusion. Assess borrower-specific changes in lifetime default risk, qualitative indicators, watchlists, arrears, and applicable policy.",
    }

def illustrative_pricing(taxonomy_aligned, min_dscr, sbti_target_pct,
                         base_margin_bps=250.0, dscr_threshold=1.25,
                         discount_bps=15.0, premium_bps=20.0) -> dict:
    """Illustrative commercial pricing sensitivity, not a market quote."""
    if taxonomy_aligned is True and sbti_target_pct >= 25.0 and min_dscr >= dscr_threshold:
        adjustment, rationale = -discount_bps, "Illustrative sustainability incentive"
    elif taxonomy_aligned is False or min_dscr < dscr_threshold:
        adjustment, rationale = premium_bps, "Illustrative risk adjustment; requires credit approval"
    else:
        adjustment, rationale = 0.0, "Neutral / insufficient basis for incentive"
    return {"base_margin_bps": base_margin_bps, "adjustment_bps": adjustment,
            "final_margin_bps": base_margin_bps + adjustment, "rationale": rationale}
