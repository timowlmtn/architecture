{{
  config(
    materialized='table'
  )
}}

select
    cast(null as varchar(100))              as event_id,
    cast(null as varchar(100))              as source_table,
    cast(null as varchar(10))               as operation,
    cast(null as jsonb)                     as primary_key_payload,
    cast(null as jsonb)                     as before_payload,
    cast(null as jsonb)                     as after_payload,
    cast(null as timestamp)                 as event_ts,
    cast(null as timestamp)                 as ingested_at
where 1 = 0
