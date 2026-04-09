#!/usr/bin/env python3
"""
pet_store_data_loader.py

Generate and upload historical backfill data and then daily operational data for a
humane pet store into the staging schema shown in the ERD.

What this script does
- Connects to PostgreSQL using environment variables
- Generates realistic synthetic data for:
    - staging.customers
    - staging.products
    - staging.orders
    - staging.order_items
    - staging.cdc_events
    - staging.raw_kinesis_events
    - staging.stg_kinesis_events
- Detects date gaps in operational sales data and fills them
- Supports:
    - historical backfill
    - daily incremental loading
- Models business behavior:
    - weekly cycle
    - peak shopping on Saturday
    - closed on Sunday
    - seasonal lifts in Spring and Fall
    - small bump around Christmas
    - closed on U.S. and Mexican holidays

Assumptions
- Tables already exist
- Schema defaults to "staging"
- The store sells humane-care products and services, not live animals
- Operational "sales" are represented by orders and order_items
- Kinesis events represent store app / fulfillment / facility telemetry
- CDC events are synthesized from inserted rows

Required environment variables
- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

Optional environment variables
- PETSTORE_SCHEMA=staging
- PETSTORE_START_DATE=2023-01-01
- PETSTORE_END_DATE=2026-04-09
- PETSTORE_MODE=auto          # auto | historical | daily | fill-gaps
- PETSTORE_DAILY_LOOKBACK_DAYS=14
- PETSTORE_RANDOM_SEED=42
"""

from __future__ import annotations

import json
import math
import os
import random
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Iterable, Sequence

import psycopg
from psycopg.rows import dict_row

import logging
import sys


def get_logger(name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger

# ----------------------------
# Configuration
# ----------------------------

UTC = timezone.utc


@dataclass(frozen=True)
class Config:
    schema: str
    start_date: date
    end_date: date
    mode: str
    daily_lookback_days: int
    random_seed: int


def get_connection() -> psycopg.Connection:
    required = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        row_factory=dict_row,
    )


def load_config() -> Config:
    today = date.today()
    schema = os.getenv("PETSTORE_SCHEMA", "staging")
    start_date = date.fromisoformat(os.getenv("PETSTORE_START_DATE", "2023-01-01"))
    end_date = date.fromisoformat(os.getenv("PETSTORE_END_DATE", today.isoformat()))
    mode = os.getenv("PETSTORE_MODE", "auto").strip().lower()
    daily_lookback_days = int(os.getenv("PETSTORE_DAILY_LOOKBACK_DAYS", "14"))
    random_seed = int(os.getenv("PETSTORE_RANDOM_SEED", "42"))

    if end_date < start_date:
        raise ValueError("PETSTORE_END_DATE cannot be before PETSTORE_START_DATE")

    if mode not in {"auto", "historical", "daily", "fill-gaps"}:
        raise ValueError("PETSTORE_MODE must be one of: auto, historical, daily, fill-gaps")

    return Config(
        schema=schema,
        start_date=start_date,
        end_date=end_date,
        mode=mode,
        daily_lookback_days=daily_lookback_days,
        random_seed=random_seed,
    )


# ----------------------------
# Holiday logic
# ----------------------------

def nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    return d + timedelta(weeks=n - 1)


def last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    if month == 12:
        d = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        d = date(year, month + 1, 1) - timedelta(days=1)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def observed_fixed_holiday(d: date) -> date:
    if d.weekday() == 5:  # Saturday
        return d - timedelta(days=1)
    if d.weekday() == 6:  # Sunday
        return d + timedelta(days=1)
    return d


def easter_sunday(year: int) -> date:
    # Anonymous Gregorian algorithm
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def us_holidays(year: int) -> set[date]:
    holidays = set()

    holidays.add(observed_fixed_holiday(date(year, 1, 1)))   # New Year's Day
    holidays.add(nth_weekday_of_month(year, 1, 0, 3))        # MLK Day
    holidays.add(nth_weekday_of_month(year, 2, 0, 3))        # Presidents Day
    holidays.add(last_weekday_of_month(year, 5, 0))          # Memorial Day
    holidays.add(observed_fixed_holiday(date(year, 6, 19)))  # Juneteenth
    holidays.add(observed_fixed_holiday(date(year, 7, 4)))   # Independence Day
    holidays.add(nth_weekday_of_month(year, 9, 0, 1))        # Labor Day
    holidays.add(nth_weekday_of_month(year, 10, 0, 2))       # Columbus Day / Indigenous Peoples
    holidays.add(observed_fixed_holiday(date(year, 11, 11))) # Veterans Day
    holidays.add(nth_weekday_of_month(year, 11, 3, 4))       # Thanksgiving
    holidays.add(observed_fixed_holiday(date(year, 12, 25))) # Christmas

    return holidays


def mexico_holidays(year: int) -> set[date]:
    holidays = set()

    holidays.add(date(year, 1, 1))                           # Año Nuevo
    holidays.add(nth_weekday_of_month(year, 2, 0, 1))       # Constitution Day (observed)
    holidays.add(nth_weekday_of_month(year, 3, 0, 3))       # Benito Juárez (observed)
    holidays.add(date(year, 5, 1))                          # Labor Day
    holidays.add(date(year, 9, 16))                         # Independence Day
    holidays.add(nth_weekday_of_month(year, 11, 0, 3))      # Revolution Day (observed)
    holidays.add(date(year, 12, 25))                        # Christmas

    # Common retail closure additions in Mexico
    easter = easter_sunday(year)
    holidays.add(easter - timedelta(days=2))                # Good Friday

    # Every six years on transition years, this can vary. Omitted by default.
    return holidays


def combined_store_holidays(year: int) -> set[date]:
    return us_holidays(year) | mexico_holidays(year)


def is_closed_day(d: date) -> bool:
    return d.weekday() == 6 or d in combined_store_holidays(d.year)  # Sunday or holiday


# ----------------------------
# Synthetic reference data
# ----------------------------

FIRST_NAMES = [
    "Olivia", "Noah", "Emma", "Liam", "Ava", "Elijah", "Sophia", "Mateo", "Isabella",
    "Lucas", "Mia", "Ethan", "Amelia", "Santiago", "Harper", "Benjamin", "Camila",
    "Daniel", "Evelyn", "Sebastian", "Sofia", "Henry", "Valentina", "Leo", "Chloe",
]

LAST_NAMES = [
    "Garcia", "Smith", "Lopez", "Johnson", "Martinez", "Brown", "Hernandez", "Davis",
    "Gonzalez", "Miller", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
    "Martin", "Lee", "Perez", "Thompson",
]

CUSTOMER_STATUSES = ["active", "active", "active", "active", "inactive", "vip"]

PRODUCT_CATALOG = [
    ("FOOD-DOG-001", "Grain-Free Dog Food", "food", "39.99"),
    ("FOOD-CAT-001", "Indoor Cat Food", "food", "27.99"),
    ("TREAT-DOG-001", "Training Treats", "treats", "8.99"),
    ("TREAT-CAT-001", "Freeze-Dried Cat Treats", "treats", "9.49"),
    ("BED-SML-001", "Small Animal Bedding", "habitat", "14.99"),
    ("HAB-RAB-001", "Rabbit Habitat Enrichment Kit", "habitat", "44.99"),
    ("TOY-DOG-001", "Natural Rubber Chew Toy", "enrichment", "12.99"),
    ("TOY-CAT-001", "Feather Wand Toy", "enrichment", "7.99"),
    ("GROOM-001", "Gentle Pet Shampoo", "grooming", "13.99"),
    ("GROOM-002", "Soft Bristle Brush", "grooming", "11.49"),
    ("WELL-001", "Paw Balm", "wellness", "10.99"),
    ("WELL-002", "Calming Chews", "wellness", "18.99"),
    ("BIRD-001", "Bird Perch Set", "habitat", "19.99"),
    ("FISH-001", "Aquarium Water Conditioner", "wellness", "6.99"),
    ("REPT-001", "Reptile Heat Lamp", "habitat", "29.99"),
    ("ADOPT-001", "New Pet Welcome Kit", "adoption_support", "49.99"),
    ("ECO-001", "Compostable Waste Bags", "supplies", "15.99"),
    ("SMALL-001", "Guinea Pig Hay Bundle", "food", "16.99"),
    ("BOWL-001", "Stainless Steel Bowl", "supplies", "9.99"),
    ("LEASH-001", "Comfort Harness & Leash", "supplies", "24.99"),
]

ORDER_STATUSES = ["placed", "placed", "placed", "placed", "fulfilled", "fulfilled", "cancelled"]
KINESIS_EVENT_TYPES = ["store_visit", "inventory_adjustment", "pickup_ready", "route_scan", "facility_ping"]
KINESIS_SOURCES = ["mobile_app", "store_pos", "warehouse_system", "delivery_router"]


# ----------------------------
# Helpers
# ----------------------------

def money(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def random_timestamp_on_day(rng: random.Random, d: date, start_hour: int = 9, end_hour: int = 19) -> datetime:
    hour = rng.randint(start_hour, end_hour)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return datetime.combine(d, time(hour, minute, second, tzinfo=UTC))


def daterange(start_d: date, end_d: date) -> Iterable[date]:
    cur = start_d
    while cur <= end_d:
        yield cur
        cur += timedelta(days=1)


def choose_weighted(rng: random.Random, items: Sequence[Any], weights: Sequence[float]) -> Any:
    return rng.choices(items, weights=weights, k=1)[0]


def seasonality_multiplier(d: date) -> float:
    # Weekly pattern:
    # Mon 0.90, Tue 0.95, Wed 1.00, Thu 1.05, Fri 1.15, Sat 1.45, Sun closed
    weekday_mult = {
        0: 0.90,
        1: 0.95,
        2: 1.00,
        3: 1.05,
        4: 1.15,
        5: 1.45,
        6: 0.00,
    }[d.weekday()]

    # Spring and Fall lift
    month_mult = 1.0
    if d.month in {3, 4, 5}:
        month_mult *= 1.18
    elif d.month in {9, 10, 11}:
        month_mult *= 1.14
    elif d.month in {1, 2, 7, 8}:
        month_mult *= 0.92

    # Small Christmas bump (first three weeks of Dec)
    christmas_mult = 1.0
    if d.month == 12 and 1 <= d.day <= 23:
        christmas_mult = 1.12

    # Mild annual noise curve
    doy = d.timetuple().tm_yday
    wave = 1.0 + 0.06 * math.sin((2 * math.pi * doy) / 365.25)

    return weekday_mult * month_mult * christmas_mult * wave


# ----------------------------
# Database setup helpers
# ----------------------------

def get_max_id(conn: psycopg.Connection, table_name: str, id_col: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COALESCE(MAX({id_col}), 0) AS max_id FROM {table_name}")
        row = cur.fetchone()
        return int(row["max_id"])


def ensure_products(conn: psycopg.Connection, schema: str) -> dict[int, dict[str, Any]]:
    table = f"{schema}.products"

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT product_id, sku, product_name, product_category, unit_price, is_active, created_at, updated_at
            FROM {table}
            ORDER BY product_id
            """
        )
        rows = cur.fetchall()

    if rows:
        return {int(r["product_id"]): dict(r) for r in rows}

    now = datetime.now(tz=UTC)
    products_to_insert = []
    for idx, (sku, name, category, price) in enumerate(PRODUCT_CATALOG, start=1):
        products_to_insert.append(
            (
                idx,
                sku,
                name,
                category,
                money(price),
                True,
                now,
                now,
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            f"""
            INSERT INTO {table}
            (
                product_id, sku, product_name, product_category, unit_price, is_active, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO NOTHING
            """,
            products_to_insert,
        )

    conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT product_id, sku, product_name, product_category, unit_price, is_active, created_at, updated_at
            FROM {table}
            ORDER BY product_id
            """
        )
        rows = cur.fetchall()

    return {int(r["product_id"]): dict(r) for r in rows}


def ensure_customers(conn: psycopg.Connection, schema: str, target_count: int = 1500) -> dict[int, dict[str, Any]]:
    table = f"{schema}.customers"

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT customer_id, email, first_name, last_name, customer_status, created_at, updated_at
            FROM {table}
            ORDER BY customer_id
            """
        )
        rows = cur.fetchall()

    existing = {int(r["customer_id"]): dict(r) for r in rows}
    if len(existing) >= target_count:
        return existing

    rng = random.Random(99173)
    max_customer_id = get_max_id(conn, table, "customer_id")
    now = datetime.now(tz=UTC)

    to_insert = []
    next_id = max_customer_id + 1
    while len(existing) + len(to_insert) < target_count:
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        suffix = rng.randint(100, 99999)
        email = f"{first.lower()}.{last.lower()}{suffix}@example.com"
        status = rng.choice(CUSTOMER_STATUSES)

        created_at = now - timedelta(days=rng.randint(5, 1200))
        updated_at = created_at + timedelta(days=rng.randint(0, 90))

        to_insert.append(
            (
                next_id,
                email,
                first,
                last,
                status,
                created_at,
                updated_at,
            )
        )
        next_id += 1

    with conn.cursor() as cur:
        get_logger().info(f"Inserting into {table}")
        cur.executemany(
            f"""
            INSERT INTO {table}
            (
                customer_id, email, first_name, last_name, customer_status, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (customer_id) DO NOTHING
            """,
            to_insert,
        )

    conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT customer_id, email, first_name, last_name, customer_status, created_at, updated_at
            FROM {table}
            ORDER BY customer_id
            """
        )
        rows = cur.fetchall()

    return {int(r["customer_id"]): dict(r) for r in rows}


# ----------------------------
# Gap detection
# ----------------------------

def existing_order_days(conn: psycopg.Connection, schema: str, start_d: date, end_d: date) -> set[date]:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT DISTINCT ordered_at::date AS order_day
            FROM {schema}.orders
            WHERE ordered_at::date BETWEEN %s AND %s
            """,
            (start_d, end_d),
        )
        return {r["order_day"] for r in cur.fetchall()}


def missing_open_days(conn: psycopg.Connection, schema: str, start_d: date, end_d: date) -> list[date]:
    existing_days = existing_order_days(conn, schema, start_d, end_d)
    missing = []
    for d in daterange(start_d, end_d):
        if is_closed_day(d):
            continue
        if d not in existing_days:
            missing.append(d)
    return missing


# ----------------------------
# Data generation
# ----------------------------

@dataclass
class LoadedBatch:
    orders: int = 0
    order_items: int = 0
    cdc_events: int = 0
    raw_kinesis_events: int = 0
    stg_kinesis_events: int = 0


def generate_daily_order_volume(d: date, rng: random.Random) -> int:
    if is_closed_day(d):
        return 0

    base = 28
    mult = seasonality_multiplier(d)
    noise = rng.uniform(0.85, 1.20)

    volume = int(round(base * mult * noise))
    return max(volume, 6)


def generate_kinesis_volume(d: date, rng: random.Random) -> int:
    if is_closed_day(d):
        return 0
    return max(8, int(generate_daily_order_volume(d, rng) * rng.uniform(0.6, 1.0)))


def generate_rows_for_day(
    d: date,
    schema: str,
    rng: random.Random,
    customer_ids: list[int],
    products: dict[int, dict[str, Any]],
    next_order_id: int,
    next_order_item_id: int,
    next_ingest_id: int,
) -> tuple[
    list[tuple[Any, ...]],
    list[tuple[Any, ...]],
    list[tuple[Any, ...]],
    list[tuple[Any, ...]],
    list[tuple[Any, ...]],
    LoadedBatch,
    int,
    int,
    int,
]:
    orders_rows: list[tuple[Any, ...]] = []
    order_items_rows: list[tuple[Any, ...]] = []
    cdc_rows: list[tuple[Any, ...]] = []
    raw_kinesis_rows: list[tuple[Any, ...]] = []
    stg_kinesis_rows: list[tuple[Any, ...]] = []

    batch = LoadedBatch()

    order_count = generate_daily_order_volume(d, rng)
    if order_count == 0:
        return (
            orders_rows,
            order_items_rows,
            cdc_rows,
            raw_kinesis_rows,
            stg_kinesis_rows,
            batch,
            next_order_id,
            next_order_item_id,
            next_ingest_id,
        )

    product_ids = list(products.keys())

    for _ in range(order_count):
        order_id = next_order_id
        next_order_id += 1

        customer_id = rng.choice(customer_ids)
        ordered_at = random_timestamp_on_day(rng, d)
        updated_at = ordered_at + timedelta(minutes=rng.randint(1, 180))
        order_status = choose_weighted(
            rng,
            ORDER_STATUSES,
            [0.38, 0.24, 0.16, 0.07, 0.10, 0.03, 0.02],
        )

        item_count = choose_weighted(rng, [1, 2, 3, 4], [0.58, 0.28, 0.11, 0.03])

        chosen_products = rng.sample(product_ids, k=min(item_count, len(product_ids)))
        line_values = []

        for product_id in chosen_products:
            qty = choose_weighted(rng, [1, 2, 3, 4], [0.70, 0.20, 0.08, 0.02])
            unit_price = money(products[product_id]["unit_price"])
            line_total = money(unit_price * qty)

            order_item_id = next_order_item_id
            next_order_item_id += 1

            order_items_rows.append(
                (
                    order_item_id,
                    order_id,
                    product_id,
                    qty,
                    unit_price,
                    line_total,
                    ordered_at,
                    updated_at,
                )
            )
            batch.order_items += 1
            line_values.append(line_total)

            cdc_rows.append(
                (
                    str(uuid.uuid4()),
                    f"{schema}.order_items",
                    "INSERT",
                    json.dumps({"order_item_id": order_item_id}),
                    None,
                    json.dumps(
                        {
                            "order_item_id": order_item_id,
                            "order_id": order_id,
                            "product_id": product_id,
                            "quantity": qty,
                            "unit_price": str(unit_price),
                            "line_total": str(line_total),
                            "created_at": ordered_at.isoformat(),
                            "updated_at": updated_at.isoformat(),
                        }
                    ),
                    updated_at,
                    datetime.now(tz=UTC),
                )
            )
            batch.cdc_events += 1

        order_total = money(sum(line_values))
        orders_rows.append(
            (
                order_id,
                customer_id,
                order_status,
                order_total,
                "USD",
                ordered_at,
                updated_at,
            )
        )
        batch.orders += 1

        cdc_rows.append(
            (
                str(uuid.uuid4()),
                f"{schema}.orders",
                "INSERT",
                json.dumps({"order_id": order_id}),
                None,
                json.dumps(
                    {
                        "order_id": order_id,
                        "customer_id": customer_id,
                        "order_status": order_status,
                        "order_total": str(order_total),
                        "currency_code": "USD",
                        "ordered_at": ordered_at.isoformat(),
                        "updated_at": updated_at.isoformat(),
                    }
                ),
                updated_at,
                datetime.now(tz=UTC),
            )
        )
        batch.cdc_events += 1

    kinesis_count = generate_kinesis_volume(d, rng)
    for _ in range(kinesis_count):
        ingest_id = next_ingest_id
        next_ingest_id += 1

        event_id = str(uuid.uuid4())
        event_type = rng.choice(KINESIS_EVENT_TYPES)
        source = rng.choice(KINESIS_SOURCES)
        event_ts = random_timestamp_on_day(rng, d, 6, 20)
        loaded_at = event_ts + timedelta(seconds=rng.randint(1, 90))

        payload = {
            "event_id": event_id,
            "event_type": event_type,
            "partition_key": f"store-{rng.randint(1, 4)}",
            "lat": f"{rng.uniform(25.0, 49.0):.6f}",
            "lon": f"{rng.uniform(-117.0, -67.0):.6f}",
            "route_id": f"R{rng.randint(100, 999)}",
            "facility_id": f"F{rng.randint(10, 40)}",
            "event_ts": event_ts.isoformat(),
            "package_id": f"P{rng.randint(100000, 999999)}",
            "source": source,
            "schema_version": "1.0",
            "payload_json": {
                "animal_safe": True,
                "temperature_ok": rng.choice([True, True, True, False]),
                "notes": rng.choice(
                    [
                        "contactless pickup complete",
                        "inventory updated",
                        "enrichment items stocked",
                        "humane carrier check passed",
                    ]
                ),
            },
        }

        raw_kinesis_rows.append(
            (
                ingest_id,
                json.dumps(payload),
                loaded_at,
            )
        )
        batch.raw_kinesis_events += 1

        stg_kinesis_rows.append(
            (
                ingest_id,
                loaded_at,
                event_id,
                event_type,
                payload["partition_key"],
                payload["lat"],
                payload["lon"],
                payload["route_id"],
                payload["facility_id"],
                event_ts,
                json.dumps(payload["payload_json"]),
                payload["package_id"],
                payload["source"],
                payload["schema_version"],
            )
        )
        batch.stg_kinesis_events += 1

    return (
        orders_rows,
        order_items_rows,
        cdc_rows,
        raw_kinesis_rows,
        stg_kinesis_rows,
        batch,
        next_order_id,
        next_order_item_id,
        next_ingest_id,
    )


# ----------------------------
# Upload logic
# ----------------------------

def insert_rows(conn: psycopg.Connection, schema: str, rows_by_table: dict[str, list[tuple[Any, ...]]]) -> None:
    with conn.cursor() as cur:
        if rows_by_table["orders"]:
            cur.executemany(
                f"""
                INSERT INTO {schema}.orders
                (
                    order_id, customer_id, order_status, order_total, currency_code, ordered_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING
                """,
                rows_by_table["orders"],
            )

        if rows_by_table["order_items"]:
            cur.executemany(
                f"""
                INSERT INTO {schema}.order_items
                (
                    order_item_id, order_id, product_id, quantity, unit_price, line_total, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_item_id) DO NOTHING
                """,
                rows_by_table["order_items"],
            )

        if rows_by_table["cdc_events"]:
            cur.executemany(
                f"""
                INSERT INTO {schema}.cdc_events
                (
                    event_id, source_table, operation, primary_key_payload, before_payload,
                    after_payload, event_ts, ingested_at
                )
                VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                rows_by_table["cdc_events"],
            )

        if rows_by_table["raw_kinesis_events"]:
            cur.executemany(
                f"""
                INSERT INTO {schema}.raw_kinesis_events
                (
                    ingest_id, raw, loaded_at
                )
                VALUES (%s, %s::jsonb, %s)
                ON CONFLICT (ingest_id) DO NOTHING
                """,
                rows_by_table["raw_kinesis_events"],
            )

    conn.commit()


def load_missing_days(
    conn: psycopg.Connection,
    cfg: Config,
    days_to_fill: list[date],
    customers: dict[int, dict[str, Any]],
    products: dict[int, dict[str, Any]],
) -> LoadedBatch:
    rng = random.Random(cfg.random_seed)

    next_order_id = get_max_id(conn, f"{cfg.schema}.orders", "order_id") + 1
    next_order_item_id = get_max_id(conn, f"{cfg.schema}.order_items", "order_item_id") + 1
    next_ingest_id = get_max_id(conn, f"{cfg.schema}.raw_kinesis_events", "ingest_id") + 1

    customer_ids = list(customers.keys())
    total = LoadedBatch()

    for d in days_to_fill:
        (
            orders_rows,
            order_items_rows,
            cdc_rows,
            raw_kinesis_rows,
            stg_kinesis_rows,
            batch,
            next_order_id,
            next_order_item_id,
            next_ingest_id,
        ) = generate_rows_for_day(
            d=d,
            schema=cfg.schema,
            rng=rng,
            customer_ids=customer_ids,
            products=products,
            next_order_id=next_order_id,
            next_order_item_id=next_order_item_id,
            next_ingest_id=next_ingest_id,
        )

        insert_rows(
            conn,
            cfg.schema,
            {
                "orders": orders_rows,
                "order_items": order_items_rows,
                "cdc_events": cdc_rows,
                "raw_kinesis_events": raw_kinesis_rows,
                "stg_kinesis_events": stg_kinesis_rows,
            },
        )

        total.orders += batch.orders
        total.order_items += batch.order_items
        total.cdc_events += batch.cdc_events
        total.raw_kinesis_events += batch.raw_kinesis_events
        total.stg_kinesis_events += batch.stg_kinesis_events

        print(
            f"[loaded {d}] orders={batch.orders} order_items={batch.order_items} "
            f"cdc_events={batch.cdc_events} raw_kinesis={batch.raw_kinesis_events} "
            f"stg_kinesis={batch.stg_kinesis_events}"
        )

    return total


# ----------------------------
# Mode selection
# ----------------------------

def determine_days_to_fill(conn: psycopg.Connection, cfg: Config) -> list[date]:
    today = date.today()

    if cfg.mode == "historical":
        return missing_open_days(conn, cfg.schema, cfg.start_date, cfg.end_date)

    if cfg.mode == "fill-gaps":
        return missing_open_days(conn, cfg.schema, cfg.start_date, cfg.end_date)

    if cfg.mode == "daily":
        start_d = max(cfg.start_date, today - timedelta(days=cfg.daily_lookback_days))
        end_d = min(cfg.end_date, today)
        return missing_open_days(conn, cfg.schema, start_d, end_d)

    # auto mode:
    # 1) If there are missing days anywhere in range, fill them
    # 2) Otherwise check recent daily window
    historical_missing = missing_open_days(conn, cfg.schema, cfg.start_date, cfg.end_date)
    if historical_missing:
        return historical_missing

    start_d = max(cfg.start_date, today - timedelta(days=cfg.daily_lookback_days))
    end_d = min(cfg.end_date, today)
    return missing_open_days(conn, cfg.schema, start_d, end_d)


# ----------------------------
# Main
# ----------------------------

def main() -> None:
    cfg = load_config()
    random.seed(cfg.random_seed)

    print(
        f"Starting pet store load: schema={cfg.schema} mode={cfg.mode} "
        f"start_date={cfg.start_date} end_date={cfg.end_date}"
    )

    with get_connection() as conn:
        products = ensure_products(conn, cfg.schema)
        customers = ensure_customers(conn, cfg.schema)

        days_to_fill = determine_days_to_fill(conn, cfg)
        if not days_to_fill:
            print("No open-day gaps detected. Nothing to load.")
            return

        print(f"Detected {len(days_to_fill)} missing open business day(s).")
        if len(days_to_fill) <= 20:
            print("Days:", ", ".join(d.isoformat() for d in days_to_fill))
        else:
            print(f"Range: {days_to_fill[0]} -> {days_to_fill[-1]}")

        total = load_missing_days(conn, cfg, days_to_fill, customers, products)

        print(
            "Load complete: "
            f"orders={total.orders}, "
            f"order_items={total.order_items}, "
            f"cdc_events={total.cdc_events}, "
            f"raw_kinesis_events={total.raw_kinesis_events}, "
            f"stg_kinesis_events={total.stg_kinesis_events}"
        )


if __name__ == "__main__":
    main()
