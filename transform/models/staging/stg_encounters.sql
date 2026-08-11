select
    cast(encounter_id as varchar) as encounter_id,
    cast(patient_id as varchar) as patient_id,
    cast(provider_id as varchar) as provider_id,
    cast(clinic_id as varchar) as clinic_id,
    cast(payer_id as varchar) as payer_id,
    cast(start_ts as timestamp) as start_ts,
    cast(end_ts as timestamp) as end_ts,
    cast(scheduled_duration_minutes as integer) as scheduled_duration_minutes,
    cast(session_type as varchar) as session_type,
    cast(status as varchar) as encounter_status,
    cast(base_encounter_cost as decimal(18,2)) as base_encounter_cost
from {{ source('landing', 'clinical_encounters') }}
