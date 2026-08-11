select
    date_trunc('month', f.encounter_date_key)::date as month_start,
    p.payer_key,
    p.payer_name,
    p.payer_type,
    count(*) as encounter_count,
    sum(f.billed_amount) as billed_amount,
    sum(f.allowed_amount) as allowed_amount,
    sum(f.reimbursement_amount) as reimbursement_amount,
    sum(f.outstanding_amount) as outstanding_amount,
    round(
        sum(case when f.claim_status = 'denied' then 1 else 0 end) * 1.0
        / nullif(sum(case when f.claim_status <> 'not_submitted' then 1 else 0 end), 0),
        4
    ) as denial_rate
from {{ ref('fct_encounters') }} f
join {{ ref('dim_payer') }} p using (payer_key)
group by 1, 2, 3, 4
