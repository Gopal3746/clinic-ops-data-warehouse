with encounters as (
    select * from {{ ref('stg_encounters') }}
),
claims as (
    select * from {{ ref('int_claims_by_encounter') }}
)
select
    md5(e.encounter_id) as encounter_key,
    e.encounter_id,
    dp.patient_key,
    dpr.provider_key,
    dc.clinic_key,
    dpay.payer_key,
    cast(e.start_ts as date) as encounter_date_key,
    e.start_ts,
    e.end_ts,
    e.session_type,
    e.encounter_status,
    e.scheduled_duration_minutes,
    case
        when e.encounter_status = 'completed'
        then greatest(0, datediff('minute', e.start_ts, e.end_ts))
        else 0
    end as actual_duration_minutes,
    coalesce(c.billed_amount, e.base_encounter_cost, 0)::decimal(18,2) as billed_amount,
    coalesce(c.allowed_amount, 0)::decimal(18,2) as allowed_amount,
    coalesce(c.reimbursement_amount, 0)::decimal(18,2) as reimbursement_amount,
    greatest(
        0,
        coalesce(c.allowed_amount, e.base_encounter_cost, 0) - coalesce(c.reimbursement_amount, 0)
    )::decimal(18,2) as outstanding_amount,
    coalesce(c.claim_status, 'not_submitted') as claim_status,
    coalesce(c.source_claim_count, 0) as source_claim_count
from encounters e
join {{ ref('dim_patient') }} dp
  on e.patient_id = dp.patient_id
 and cast(e.start_ts as date) >= dp.effective_from
 and cast(e.start_ts as date) < coalesce(dp.effective_to, date '9999-12-31')
join {{ ref('dim_provider') }} dpr
  on e.provider_id = dpr.provider_id
join {{ ref('dim_clinic_location') }} dc
  on e.clinic_id = dc.clinic_id
join {{ ref('dim_payer') }} dpay
  on e.payer_id = dpay.payer_id
left join claims c
  on e.encounter_id = c.encounter_id
