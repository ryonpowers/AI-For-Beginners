"""
ingestion/ingest_report_catalog.py
────────────────────────────────────
Loads a Turtle report catalog file into Stardog as
the named graph <urn:reports:catalog>.

Environment variables required:
  STARDOG_ENDPOINT
  STARDOG_DB
  STARDOG_USER
  STARDOG_PASSWORD

Optional:
  REPORT_CATALOG_FILE – path to .ttl file (default: data/samples/report_catalog.ttl)
"""

import os
import sys
from pathlib import Path

import requests

ENDPOINT = os.environ["STARDOG_ENDPOINT"].rstrip("/")
DB = os.environ["STARDOG_DB"]
USER = os.environ["STARDOG_USER"]
PASSWORD = os.environ["STARDOG_PASSWORD"]

CATALOG_FILE = Path(
    os.environ.get(
        "REPORT_CATALOG_FILE",
        Path(__file__).parent.parent / "data" / "samples" / "report_catalog.ttl",
    )
)

NAMED_GRAPH = "urn:reports:catalog"


def load_to_stardog(turtle: str, named_graph: str) -> None:
    url = f"{ENDPOINT}/{DB}/data"
    headers = {"Content-Type": "text/turtle"}
    resp = requests.post(
        url,
        params={"graph-uri": named_graph},
        data=turtle.encode("utf-8"),
        headers=headers,
        auth=(USER, PASSWORD),
        timeout=30,
    )
    resp.raise_for_status()
    print(f"Loaded {len(turtle)} bytes into <{named_graph}>  HTTP {resp.status_code}")


def main() -> None:
    if not CATALOG_FILE.exists():
        print(f"ERROR: Catalog file not found: {CATALOG_FILE}", file=sys.stderr)
        sys.exit(1)

    turtle = CATALOG_FILE.read_text(encoding="utf-8")
    print(f"Loaded catalog from {CATALOG_FILE}")
    load_to_stardog(turtle, NAMED_GRAPH)
    print("Done.")


if __name__ == "__main__":
    main()
