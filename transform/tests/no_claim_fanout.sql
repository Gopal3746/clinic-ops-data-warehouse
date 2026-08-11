select encounter_id
from {{ ref('fct_encounters') }}
group by 1
having count(*) > 1
