{{
  config(
    materialized='table'
  )
}}

select
    cast(null as bigint)                    as order_id,
    cast(null as bigint)                    as customer_id,
    cast(null as varchar(30))               as order_status,
    cast(null as numeric(12,2))             as order_total,
    cast(null as varchar(3))                as currency_code,
    cast(null as timestamp)                 as ordered_at,
    cast(null as timestamp)                 as updated_at
where 1 = 0
