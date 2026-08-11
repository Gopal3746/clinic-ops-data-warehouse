with bounds as (
    select min(cast(start_ts as date)) as min_date, max(cast(start_ts as date)) as max_date
    from {{ ref('stg_encounters') }}
),
dates as (
    select cast(d as date) as date_day
    from bounds,
    generate_series(min_date, max_date, interval 1 day) as t(d)
)
select
    date_day as date_key,
    extract(year from date_day)::integer as year,
    extract(quarter from date_day)::integer as quarter,
    extract(month from date_day)::integer as month_number,
    strftime(date_day, '%B') as month_name,
    date_trunc('month', date_day)::date as month_start,
    extract(week from date_day)::integer as week_number,
    extract(dow from date_day)::integer as day_of_week_number,
    strftime(date_day, '%A') as day_name
from dates
