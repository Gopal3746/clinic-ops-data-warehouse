select
    md5(p.patient_id || '|' || cast(h.effective_from as varchar)) as patient_key,
    p.patient_id,
    p.birth_date,
    p.sex,
    h.city,
    h.state,
    h.preferred_language,
    h.payer_id,
    h.effective_from,
    h.effective_to,
    h.is_current
from {{ ref('stg_patient_profile_history') }} h
join {{ ref('stg_patients') }} p
  on h.patient_id = p.patient_id
