SOURCE_ENTITIES = {
    "clinical": ["patients", "providers", "clinics", "encounters"],
    "crm": ["patient_profile_history", "referrals"],
    "finance": ["payers", "claims"],
}

LANDING_TABLES = {
    ("clinical", "patients"): "clinical_patients",
    ("clinical", "providers"): "clinical_providers",
    ("clinical", "clinics"): "clinical_clinics",
    ("clinical", "encounters"): "clinical_encounters",
    ("crm", "patient_profile_history"): "crm_patient_profile_history",
    ("crm", "referrals"): "crm_referrals",
    ("finance", "payers"): "finance_payers",
    ("finance", "claims"): "finance_claims",
}
