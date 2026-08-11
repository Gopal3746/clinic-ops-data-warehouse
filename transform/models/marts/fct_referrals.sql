select
    md5(r.referral_id) as referral_key,
    r.referral_id,
    dp.patient_key,
    dc.clinic_key,
    r.referral_date as referral_date_key,
    r.source_channel,
    r.referral_status,
    r.intake_scheduled_at,
    r.converted_at,
    case when r.intake_scheduled_at is not null then 1 else 0 end as intake_scheduled_flag,
    case when r.converted_at is not null then 1 else 0 end as converted_flag
from {{ ref('stg_referrals') }} r
join {{ ref('dim_patient') }} dp
  on r.patient_id = dp.patient_id
 and r.referral_date >= dp.effective_from
 and r.referral_date < coalesce(dp.effective_to, date '9999-12-31')
join {{ ref('dim_clinic_location') }} dc
  on r.clinic_id = dc.clinic_id
