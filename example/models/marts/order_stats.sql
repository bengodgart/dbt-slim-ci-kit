with orders as (
    select * from {{ ref('orders') }}
)

select
    status,
    count(*) as order_count,
    round(sum(amount_usd), 2) as total_amount_usd,
    round(avg(amount_usd), 2) as avg_amount_usd
from orders
group by 1
