# Data Dictionary

## `marts.fct_encounters`

**Grain:** one row per encounter/session.

| Column | Meaning |
|---|---|
| `encounter_key` | warehouse surrogate key |
| `encounter_id` | source encounter ID |
| `patient_key` | SCD2 patient version valid on encounter date |
| `provider_key` | provider dimension key |
| `clinic_key` | clinic dimension key |
| `payer_key` | payer dimension key |
| `encounter_date_key` | calendar date |
| `scheduled_duration_minutes` | scheduled appointment duration |
| `actual_duration_minutes` | completed-care duration; zero for non-completed |
| `billed_amount` | claim billed amount, otherwise encounter base cost |
| `allowed_amount` | payer allowed amount; zero when not submitted |
| `reimbursement_amount` | amount reimbursed |
| `outstanding_amount` | allowed/base amount less reimbursement, floored at zero |
| `claim_status` | paid, pending, denied, partial, or not_submitted |

## `marts.dim_patient`

**Type:** SCD Type 2.

A natural `patient_id` may have multiple rows. `effective_from` is inclusive; `effective_to` is exclusive; a null `effective_to` indicates the current version.

The dimension deliberately excludes names and street addresses because the reporting use case does not require them.

## `marts.fct_referrals`

**Grain:** one row per referral.

Used for referral → intake → conversion reporting by clinic and source channel.

## Reporting marts

- `mart_clinic_utilization_monthly`
- `mart_payer_financials_monthly`
- `mart_referral_funnel_monthly`
