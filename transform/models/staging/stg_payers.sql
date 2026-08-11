select
    cast(payer_id as varchar) as payer_id,
    cast(payer_name as varchar) as payer_name,
    cast(payer_type as varchar) as payer_type
from {{ source('landing', 'finance_payers') }}
