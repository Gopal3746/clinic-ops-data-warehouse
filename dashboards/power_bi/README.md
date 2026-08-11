# Power BI Build Guide

This folder defines the Power BI artifact to build against the DuckDB marts.

## Recommended tables/views

Import:

- `marts.fct_encounters`
- `marts.fct_referrals`
- `marts.dim_patient`
- `marts.dim_provider`
- `marts.dim_clinic_location`
- `marts.dim_payer`
- `marts.dim_date`
- `marts.mart_clinic_utilization_monthly`
- `marts.mart_payer_financials_monthly`
- `marts.mart_referral_funnel_monthly`

## Relationships

Use single-direction one-to-many relationships from each dimension to each fact:

- `dim_patient[patient_key]` → `fct_encounters[patient_key]`
- `dim_provider[provider_key]` → `fct_encounters[provider_key]`
- `dim_clinic_location[clinic_key]` → `fct_encounters[clinic_key]`
- `dim_payer[payer_key]` → `fct_encounters[payer_key]`
- `dim_date[date_key]` → `fct_encounters[encounter_date_key]`
- `dim_patient[patient_key]` → `fct_referrals[patient_key]`
- `dim_clinic_location[clinic_key]` → `fct_referrals[clinic_key]`
- `dim_date[date_key]` → `fct_referrals[referral_date_key]`

Mark `dim_date[date_key]` as the date table.

## Report page 1 — Clinic Utilization

Cards:
- Total Encounters
- Completed Encounters
- Completed Care Hours
- No-Show Rate

Visuals:
- line chart: month → Completed Encounters
- clustered bar: clinic → Completed Care Hours
- matrix: provider specialty × clinic → completed encounters / no-show rate
- slicers: month, state, clinic, specialty

## Report page 2 — Payer Financials

Cards:
- Billed Amount
- Allowed Amount
- Reimbursement Amount
- Outstanding Amount
- Reimbursement Rate
- Denial Rate

Visuals:
- line chart: month → billed and reimbursed
- bar chart: payer → outstanding
- matrix: payer type × claim status
- slicers: month, payer, payer type, clinic

## Report page 3 — Referral Funnel

Cards:
- Referrals
- Intake Scheduled
- Converted Referrals
- Referral Conversion Rate

Visuals:
- funnel: referral → intake scheduled → converted
- line chart: month → conversion rate
- bar chart: source channel → referrals and conversions
- slicers: month, clinic, source channel

## Validation before screenshots

- Total encounter count in Power BI must equal `select count(*) from marts.fct_encounters`.
- Total reimbursement must match the warehouse query exactly.
- Filter one clinic and one month, then validate the visual values against SQL.
- Use only synthetic-data screenshots.
