{{
  config(
    materialized='table'
  )
}}

select
    cast(null as bigint)                    as order_item_id,
    cast(null as bigint)                    as order_id,
    cast(null as bigint)                    as product_id,
    cast(null as integer)                   as quantity,
    cast(null as numeric(12,2))             as unit_price,
    cast(null as numeric(12,2))             as line_total,
    cast(null as timestamp)                 as created_at,
    cast(null as timestamp)                 as updated_at
where 1 = 0
