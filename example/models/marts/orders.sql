with orders as (
    select * from {{ ref('stg_orders') }}
)

select
    order_id,
    customer_id,
    order_date,
    status,
    amount_usd,
    case when status = 'returned' then true else false end as is_returned
from orders
