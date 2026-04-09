-- =========================
-- PRODUCTS
-- =========================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'products_pkey'
    ) THEN
        ALTER TABLE staging.products
        ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);
    END IF;
END $$;


-- =========================
-- CUSTOMERS
-- =========================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'customer_pkey'
    ) THEN
        ALTER TABLE staging.customers
        ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'orders_pkey'
    ) THEN
        ALTER TABLE staging.orders
        ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'order_items_pkey'
    ) THEN
        ALTER TABLE staging.order_items
        ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_item_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'raw_kinesis_events_pkey'
    ) THEN
        ALTER TABLE staging.raw_kinesis_events
        ADD CONSTRAINT raw_kinesis_events_pkey PRIMARY KEY (ingest_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'orders_customer_fk'
    ) THEN
        ALTER TABLE staging.orders
        ADD CONSTRAINT orders_customer_fk
        FOREIGN KEY (customer_id)
        REFERENCES staging.customers(customer_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'order_items_order_fk'
    ) THEN
        ALTER TABLE staging.order_items
        ADD CONSTRAINT order_items_order_fk
        FOREIGN KEY (order_id)
        REFERENCES staging.orders(order_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'order_items_product_fk'
    ) THEN
        ALTER TABLE staging.order_items
        ADD CONSTRAINT order_items_product_fk
        FOREIGN KEY (product_id)
        REFERENCES staging.products(product_id);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'products_sku_key'
    ) THEN
        ALTER TABLE staging.products
        ADD CONSTRAINT products_sku_key UNIQUE (sku);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'customers_email_key'
    ) THEN
        ALTER TABLE staging.customers
        ADD CONSTRAINT customers_email_key UNIQUE (email);
    END IF;
END $$;


DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'event_id_pkey'
    ) THEN
        ALTER TABLE staging.cdc_events
        ADD CONSTRAINT event_id_pkey PRIMARY KEY (event_id);
    END IF;
END $$;