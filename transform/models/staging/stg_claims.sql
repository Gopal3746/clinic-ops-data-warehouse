select
    cast(claim_id as varchar) as claim_id,
    cast(encounter_id as varchar) as encounter_id,
    cast(patient_id as varchar) as patient_id,
    cast(payer_id as varchar) as payer_id,
    cast(submitted_at as timestamp) as submitted_at,
    cast(paid_at as timestamp) as paid_at,
    cast(billed_amount as decimal(18,2)) as billed_amount,
    cast(allowed_amount as decimal(18,2)) as allowed_amount,
    cast(reimbursement_amount as decimal(18,2)) as reimbursement_amount,
    cast(claim_status as varchar) as claim_status
from {{ source('landing', 'finance_claims') }}
