select
    md5(clinic_id) as clinic_key,
    clinic_id,
    clinic_name,
    city,
    state,
    timezone
from {{ ref('stg_clinics') }}
