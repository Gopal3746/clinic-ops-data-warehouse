select
    cast(patient_id as varchar) as patient_id,
    cast(birth_date as date) as birth_date,
    cast(sex as varchar) as sex,
    cast(created_at as timestamp) as created_at
from {{ source('landing', 'clinical_patients') }}
