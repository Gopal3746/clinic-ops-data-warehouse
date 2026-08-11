select
    cast(clinic_id as varchar) as clinic_id,
    cast(clinic_name as varchar) as clinic_name,
    cast(city as varchar) as city,
    cast(state as varchar) as state,
    cast(timezone as varchar) as timezone
from {{ source('landing', 'clinical_clinics') }}
