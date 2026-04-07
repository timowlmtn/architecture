{{
  config(
    materialized='table'
  )
}}

select
    cast(null as bigint)                    as product_id,
    cast(null as varchar(100))              as sku,
    cast(null as varchar(255))              as product_name,
    cast(null as varchar(100))              as product_category,
    cast(null as numeric(12,2))             as unit_price,
    cast(null as boolean)                   as is_active,
    cast(null as timestamp)                 as created_at,
    cast(null as timestamp)                 as updated_at
where 1 = 0
