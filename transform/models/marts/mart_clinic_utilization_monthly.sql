select
    date_trunc('month', f.encounter_date_key)::date as month_start,
    c.clinic_key,
    c.clinic_name,
    c.state,
    count(*) as scheduled_encounters,
    sum(case when f.encounter_status = 'completed' then 1 else 0 end) as completed_encounters,
    sum(case when f.encounter_status = 'no_show' then 1 else 0 end) as no_show_encounters,
    round(sum(f.scheduled_duration_minutes) / 60.0, 2) as scheduled_hours,
    round(sum(f.actual_duration_minutes) / 60.0, 2) as completed_care_hours,
    round(
        sum(case when f.encounter_status = 'no_show' then 1 else 0 end) * 1.0 / nullif(count(*), 0),
        4
    ) as no_show_rate
from {{ ref('fct_encounters') }} f
join {{ ref('dim_clinic_location') }} c using (clinic_key)
group by 1, 2, 3, 4
