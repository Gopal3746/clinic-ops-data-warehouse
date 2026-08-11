select
    cast(provider_id as varchar) as provider_id,
    cast(clinic_id as varchar) as clinic_id,
    cast(specialty as varchar) as specialty,
    cast(employment_type as varchar) as employment_type,
    cast(weekly_capacity_hours as integer) as weekly_capacity_hours,
    cast(active_flag as boolean) as active_flag
from {{ source('landing', 'clinical_providers') }}
