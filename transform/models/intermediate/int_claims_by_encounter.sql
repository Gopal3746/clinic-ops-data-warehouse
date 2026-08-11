select
    encounter_id,
    max(patient_id) as patient_id,
    max(payer_id) as payer_id,
    sum(billed_amount) as billed_amount,
    sum(allowed_amount) as allowed_amount,
    sum(reimbursement_amount) as reimbursement_amount,
    max(claim_status) as claim_status,
    count(*) as source_claim_count
from {{ ref('stg_claims') }}
group by 1
