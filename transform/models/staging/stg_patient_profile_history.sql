select
    cast(patient_id as varchar) as patient_id,
    cast(city as varchar) as city,
    cast(state as varchar) as state,
    cast(preferred_language as varchar) as preferred_language,
    cast(payer_id as varchar) as payer_id,
    cast(effective_from as date) as effective_from,
    cast(effective_to as date) as effective_to,
    cast(is_current as boolean) as is_current
from {{ source('landing', 'crm_patient_profile_history') }}
