"""Transparent configuration for the illustrative ClimateCredit model."""
from dataclasses import dataclass

USD_HKD = 7.8  # Illustrative fixed conversion assumption; replace with dated market FX.
BASE_INTEREST_RATE = 0.06
ANNUAL_PRINCIPAL_REPAYMENT_SHARE_OF_SUBJECT_LOAN = 0.10
PROJECTION_YEARS = 5
DSCR_SCREENING_LEVEL = 1.25  # Illustrative internal screening level, not a universal regulatory rule.
BASE_MARGIN_BPS = 250.0
ILLUSTRATIVE_SLL_DISCOUNT_BPS = 15.0
ILLUSTRATIVE_RISK_PREMIUM_BPS = 20.0

TAXONOMY_FRAMEWORKS = {
    "Hong Kong Taxonomy for Sustainable Finance": {
        "mode": "manual",
        "description": "Framework-specific technical screening criteria and activity eligibility must be checked against the applicable published version. This demo does not claim automatic alignment.",
        "source": "https://www.hkma.gov.hk/eng/key-functions/international-financial-centre/green-and-sustainable-finance/",
    },
    "EU Taxonomy": {
        "mode": "manual",
        "description": "Eligibility and alignment depend on the economic activity, applicable technical screening criteria, DNSH and minimum safeguards. This demo records evidence status only.",
        "source": "https://finance.ec.europa.eu/sustainable-finance/tools-and-standards/eu-taxonomy-sustainable-activities_en",
    },
    "Custom internal policy (configurable thresholds)": {
        "mode": "thresholds",
        "description": "Illustrative internal screening thresholds only; not a statutory taxonomy determination.",
        "source": "",
    },
}
