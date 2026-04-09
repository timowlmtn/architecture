#!/usr/bin/env python3
"""
Generate a Mermaid ER diagram from PostgreSQL schemas.

Environment variables:
    POSTGRES_HOST
    POSTGRES_PORT
    POSTGRES_DB
    POSTGRES_USER
    POSTGRES_PASSWORD

Usage:
    python pg_to_mermaid.py --schema public
    python pg_to_mermaid.py --schema public analytics
    python pg_to_mermaid.py --schema public --output schema.mmd
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple

import psycopg


@dataclass
class Column:
    schema_name: str
    table_name: str
    column_name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool


@dataclass
class ForeignKey:
    fk_name: str
    source_schema: str
    source_table: str
    source_column: str
    target_schema: str
    target_table: str
    target_column: str


def sanitize_identifier(name: str) -> str:
    """
    Mermaid identifiers should be simple and stable.
    Convert schema.table -> schema_table and strip odd characters.
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if re.match(r"^[0-9]", cleaned):
        cleaned = f"t_{cleaned}"
    return cleaned


def mermaid_type(pg_type: str) -> str:
    """
    Map PostgreSQL types to Mermaid-friendly types.
    """
    t = pg_type.lower()

    mappings = [
        ("bigint", "BIGINT"),
        ("integer", "INT"),
        ("smallint", "SMALLINT"),
        ("numeric", "NUMERIC"),
        ("decimal", "DECIMAL"),
        ("double precision", "FLOAT"),
        ("real", "FLOAT"),
        ("boolean", "BOOLEAN"),
        ("timestamp with time zone", "TIMESTAMPTZ"),
        ("timestamp without time zone", "TIMESTAMP"),
        ("date", "DATE"),
        ("time with time zone", "TIMETZ"),
        ("time without time zone", "TIME"),
        ("uuid", "UUID"),
        ("jsonb", "JSONB"),
        ("json", "JSON"),
        ("text", "TEXT"),
        ("character varying", "VARCHAR"),
        ("character", "CHAR"),
        ("bytea", "BYTEA"),
    ]

    for prefix, label in mappings:
        if t.startswith(prefix):
            return label

    return pg_type.upper().replace(" ", "_")


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
    )


def fetch_columns(conn: psycopg.Connection, schemas: List[str]) -> List[Column]:
    query = """
    WITH pk_cols AS (
        SELECT
            tc.table_schema,
            tc.table_name,
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
         AND tc.table_name = kcu.table_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = ANY(%s)
    )
    SELECT
        c.table_schema,
        c.table_name,
        c.column_name,
        c.data_type,
        (c.is_nullable = 'YES') AS is_nullable,
        (pk.column_name IS NOT NULL) AS is_primary_key
    FROM information_schema.columns c
    LEFT JOIN pk_cols pk
      ON c.table_schema = pk.table_schema
     AND c.table_name = pk.table_name
     AND c.column_name = pk.column_name
    WHERE c.table_schema = ANY(%s)
    ORDER BY c.table_schema, c.table_name, c.ordinal_position
    """

    with conn.cursor() as cur:
        cur.execute(query, (schemas, schemas))
        rows = cur.fetchall()

    return [
        Column(
            schema_name=row[0],
            table_name=row[1],
            column_name=row[2],
            data_type=row[3],
            is_nullable=row[4],
            is_primary_key=row[5],
        )
        for row in rows
    ]


def fetch_foreign_keys(
    conn: psycopg.Connection, schemas: List[str]
) -> List[ForeignKey]:
    query = """
    SELECT
        tc.constraint_name,
        kcu.table_schema AS source_schema,
        kcu.table_name AS source_table,
        kcu.column_name AS source_column,
        ccu.table_schema AS target_schema,
        ccu.table_name AS target_table,
        ccu.column_name AS target_column
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name
     AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
      ON tc.constraint_name = ccu.constraint_name
     AND tc.table_schema = ccu.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
      AND (
            kcu.table_schema = ANY(%s)
         OR ccu.table_schema = ANY(%s)
      )
    ORDER BY source_schema, source_table, tc.constraint_name, source_column
    """

    with conn.cursor() as cur:
        cur.execute(query, (schemas, schemas))
        rows = cur.fetchall()

    return [
        ForeignKey(
            fk_name=row[0],
            source_schema=row[1],
            source_table=row[2],
            source_column=row[3],
            target_schema=row[4],
            target_table=row[5],
            target_column=row[6],
        )
        for row in rows
    ]


def group_columns(columns: List[Column]) -> Dict[Tuple[str, str], List[Column]]:
    grouped: Dict[Tuple[str, str], List[Column]] = {}
    for col in columns:
        key = (col.schema_name, col.table_name)
        grouped.setdefault(key, []).append(col)
    return grouped


def build_mermaid(columns: List[Column], foreign_keys: List[ForeignKey]) -> str:
    grouped = group_columns(columns)

    alias_map: Dict[Tuple[str, str], str] = {}
    for schema_name, table_name in grouped:
        alias_map[(schema_name, table_name)] = sanitize_identifier(
            f"{schema_name}_{table_name}"
        )

    lines: List[str] = []
    lines.append("erDiagram")

    # Entities
    for (schema_name, table_name), cols in sorted(grouped.items()):
        alias = alias_map[(schema_name, table_name)]
        lines.append(f"    {alias} {{")
        for col in cols:
            dtype = mermaid_type(col.data_type)
            flags = []
            if col.is_primary_key:
                flags.append("PK")
            if not col.is_nullable:
                flags.append("NOT NULL")

            flag_text = f' "{", ".join(flags)}"' if flags else ""
            lines.append(
                f"        {dtype} {sanitize_identifier(col.column_name)}{flag_text}"
            )
        lines.append("    }")
        lines.append(f"    %% {alias} = {schema_name}.{table_name}")

    # Relationships
    seen_relationships = set()
    for fk in foreign_keys:
        source_key = (fk.source_schema, fk.source_table)
        target_key = (fk.target_schema, fk.target_table)

        if source_key not in alias_map or target_key not in alias_map:
            continue

        source_alias = alias_map[source_key]
        target_alias = alias_map[target_key]

        rel_key = (
            source_alias,
            target_alias,
            fk.source_column,
            fk.target_column,
            fk.fk_name,
        )
        if rel_key in seen_relationships:
            continue
        seen_relationships.add(rel_key)

        label = f'"{fk.fk_name}: {fk.source_column} -> {fk.target_column}"'
        lines.append(f"    {target_alias} ||--o{{ {source_alias} : {label}")

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Mermaid ER diagram from PostgreSQL schemas."
    )
    parser.add_argument(
        "--schema",
        nargs="+",
        required=True,
        help="One or more schema names to inspect.",
    )
    parser.add_argument(
        "--output",
        default="schema_er_diagram.mmd",
        help="Output Mermaid file path. Default: schema_er_diagram.mmd",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        with get_connection() as conn:
            columns = fetch_columns(conn, args.schema)
            foreign_keys = fetch_foreign_keys(conn, args.schema)

        if not columns:
            print(
                f"No tables found in schema(s): {', '.join(args.schema)}",
                file=sys.stderr,
            )
            return 1

        mermaid = build_mermaid(columns, foreign_keys)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(mermaid)

        print(f"Mermaid ER diagram written to: {args.output}")
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
