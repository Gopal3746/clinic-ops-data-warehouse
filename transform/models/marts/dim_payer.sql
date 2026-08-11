select
    md5(payer_id) as payer_key,
    payer_id,
    payer_name,
    payer_type
from {{ ref('stg_payers') }}
