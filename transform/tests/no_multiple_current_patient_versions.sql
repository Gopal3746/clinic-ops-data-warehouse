select patient_id
from {{ ref('dim_patient') }}
where is_current
group by 1
having count(*) > 1
