select
    md5(provider_id) as provider_key,
    provider_id,
    clinic_id,
    specialty,
    employment_type,
    weekly_capacity_hours,
    active_flag
from {{ ref('stg_providers') }}
