select
    cast(referral_id as varchar) as referral_id,
    cast(patient_id as varchar) as patient_id,
    cast(clinic_id as varchar) as clinic_id,
    cast(referral_date as date) as referral_date,
    cast(source_channel as varchar) as source_channel,
    cast(referral_status as varchar) as referral_status,
    cast(intake_scheduled_at as timestamp) as intake_scheduled_at,
    cast(converted_at as timestamp) as converted_at
from {{ source('landing', 'crm_referrals') }}
