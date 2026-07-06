with source as (
    select * from {{ ref('raw_orders') }}
)

select
    id as order_id,
    customer_id,
    order_date,
    status,
    amount_cents,
    amount_cents / 100.0 as amount_usd,
    upper(status) as status_display
from source
