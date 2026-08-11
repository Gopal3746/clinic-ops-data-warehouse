select
    date_trunc('month', r.referral_date_key)::date as month_start,
    c.clinic_key,
    c.clinic_name,
    r.source_channel,
    count(*) as referrals,
    sum(r.intake_scheduled_flag) as intake_scheduled,
    sum(r.converted_flag) as converted,
    round(sum(r.converted_flag) * 1.0 / nullif(count(*), 0), 4) as conversion_rate
from {{ ref('fct_referrals') }} r
join {{ ref('dim_clinic_location') }} c using (clinic_key)
group by 1, 2, 3, 4
