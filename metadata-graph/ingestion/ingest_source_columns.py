"""
ingestion/ingest_source_columns.py
────────────────────────────────────
Queries INFORMATION_SCHEMA from one or more SQL Server databases and loads
the resulting column metadata into Stardog as the named graph
<urn:source:columns>.

Environment variables required:
  STARDOG_ENDPOINT  – e.g. http://localhost:5820
  STARDOG_DB        – Stardog database name
  STARDOG_USER
  STARDOG_PASSWORD
  SQL_CONNECTION    – pyodbc connection string for the source SQL Server

Optional:
  SQL_DATABASES     – comma-separated list of DB names to scan (default: all)
"""

import io
import os
import sys
from urllib.parse import quote

import pyodbc
import requests

# ── Config ────────────────────────────────────────────────────────────────
ENDPOINT = os.environ["STARDOG_ENDPOINT"].rstrip("/")
DB = os.environ["STARDOG_DB"]
USER = os.environ["STARDOG_USER"]
PASSWORD = os.environ["STARDOG_PASSWORD"]
SQL_CONN_STR = os.environ["SQL_CONNECTION"]
SQL_DATABASES = [d.strip() for d in os.environ.get("SQL_DATABASES", "").split(",") if d.strip()]

NAMED_GRAPH = "urn:source:columns"
BM = "urn:org:metadata:"
XSD = "http://www.w3.org/2001/XMLSchema#"


def _uri(*parts: str) -> str:
    slug = "_".join(quote(p, safe="") for p in parts)
    return f"<{BM}{slug}>"


def _lit(value: str) -> str:
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


COLUMN_QUERY = """
SELECT
    TABLE_CATALOG,
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
ORDER BY TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
"""


def fetch_columns(conn_str: str, databases: list[str]) -> list[dict]:
    rows = []
    conn = pyodbc.connect(conn_str, autocommit=True)
    cursor = conn.cursor()

    if databases:
        db_list = databases
    else:
        cursor.execute("SELECT name FROM sys.databases WHERE state_desc = 'ONLINE' AND name NOT IN ('master','tempdb','model','msdb')")
        db_list = [r[0] for r in cursor.fetchall()]

    for db_name in db_list:
        try:
            cursor.execute(f"USE [{db_name}]")
            cursor.execute(COLUMN_QUERY)
            for r in cursor.fetchall():
                rows.append({
                    "catalog": r[0],
                    "schema": r[1],
                    "table": r[2],
                    "column": r[3],
                    "data_type": r[4],
                    "nullable": r[5],
                })
        except pyodbc.Error as exc:
            print(f"WARN: skipping database {db_name}: {exc}", file=sys.stderr)

    conn.close()
    return rows


def build_turtle(rows: list[dict]) -> str:
    buf = io.StringIO()
    buf.write(f"@prefix bm:  <{BM}> .\n")
    buf.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
    buf.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")

    db_seen: set[str] = set()
    schema_seen: set[str] = set()
    table_seen: set[str] = set()

    for r in rows:
        cat, sch, tbl, col, dtype = r["catalog"], r["schema"], r["table"], r["column"], r["data_type"]

        db_uri = _uri("db", cat)
        schema_uri = _uri("schema", cat, sch)
        table_uri = _uri("table", cat, sch, tbl)
        col_uri = _uri("col", cat, sch, tbl, col)

        if db_uri not in db_seen:
            db_seen.add(db_uri)
            buf.write(f"{db_uri} a bm:SourceDatabase ;\n    bm:databaseName {_lit(cat)} .\n\n")

        if schema_uri not in schema_seen:
            schema_seen.add(schema_uri)
            buf.write(f"{schema_uri} a bm:SourceSchema ;\n    bm:schemaName {_lit(sch)} .\n")
            buf.write(f"{db_uri} bm:hasSchema {schema_uri} .\n\n")

        if table_uri not in table_seen:
            table_seen.add(table_uri)
            buf.write(f"{table_uri} a bm:SourceTable ;\n    bm:tableName {_lit(tbl)} .\n")
            buf.write(f"{schema_uri} bm:hasTable {table_uri} .\n\n")

        buf.write(f"{col_uri} a bm:SourceColumn ;\n")
        buf.write(f"    bm:columnName {_lit(col)} ;\n")
        buf.write(f"    bm:dataType {_lit(dtype)} .\n")
        buf.write(f"{table_uri} bm:hasColumn {col_uri} .\n\n")

    return buf.getvalue()


def load_to_stardog(turtle: str, named_graph: str) -> None:
    url = f"{ENDPOINT}/{DB}/data"
    headers = {"Content-Type": "text/turtle"}
    resp = requests.post(
        url,
        params={"graph-uri": named_graph},
        data=turtle.encode("utf-8"),
        headers=headers,
        auth=(USER, PASSWORD),
        timeout=60,
    )
    resp.raise_for_status()
    print(f"Loaded {len(turtle)} bytes into <{named_graph}>  HTTP {resp.status_code}")


def main() -> None:
    print("Fetching column metadata from SQL Server...")
    rows = fetch_columns(SQL_CONN_STR, SQL_DATABASES)
    print(f"Fetched {len(rows)} columns.")
    turtle = build_turtle(rows)
    load_to_stardog(turtle, NAMED_GRAPH)
    print("Done.")


if __name__ == "__main__":
    main()
