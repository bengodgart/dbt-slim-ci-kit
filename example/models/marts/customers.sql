with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

order_rollup as (
    select
        customer_id,
        count(*) as order_count,
        sum(amount_usd) as lifetime_amount_usd,
        max(order_date) as most_recent_order_date
    from orders
    group by 1
)

select
    c.customer_id,
    c.full_name,
    c.signup_date,
    coalesce(o.order_count, 0) as order_count,
    coalesce(o.lifetime_amount_usd, 0) as lifetime_amount_usd,
    o.most_recent_order_date
from customers as c
left join order_rollup as o on c.customer_id = o.customer_id
