{{
  config(
    materialized='table'
  )
}}

select
    cast(null as bigint)           as customer_id,
    cast(null as varchar(255))     as email,
    cast(null as varchar(100))     as first_name,
    cast(null as varchar(100))     as last_name,
    cast(null as varchar(30))      as customer_status,
    cast(null as timestamp)        as created_at,
    cast(null as timestamp)        as updated_at
where false