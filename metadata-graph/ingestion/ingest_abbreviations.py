"""
ingestion/ingest_abbreviations.py
──────────────────────────────────
Reads the IT-approved abbreviation CSV and loads it into Stardog
as the named graph <urn:abbrev:mapping>.

Environment variables required:
  STARDOG_ENDPOINT  – e.g. http://localhost:5820
  STARDOG_DB        – database name
  STARDOG_USER      – username
  STARDOG_PASSWORD  – password

Optional:
  ABBREV_FILE       – path to CSV (default: data/samples/abbreviations.csv)
  ABBREV_FILE_ID    – version tag for the AbbreviationFile node
  ABBREV_APPROVED_DATE – ISO date of org approval (default: today)
"""

import csv
import io
import os
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

import requests

# ── Config from environment (read at call time, not import time) ───────────
def _config() -> dict:
    return {
        "endpoint": os.environ["STARDOG_ENDPOINT"].rstrip("/"),
        "db": os.environ["STARDOG_DB"],
        "user": os.environ["STARDOG_USER"],
        "password": os.environ["STARDOG_PASSWORD"],
        "abbrev_file": Path(
            os.environ.get(
                "ABBREV_FILE",
                Path(__file__).parent.parent / "data" / "samples" / "abbreviations.csv",
            )
        ),
        "file_id": os.environ.get("ABBREV_FILE_ID", "IT-AbbreviationFile-v1"),
        "approved_date": os.environ.get("ABBREV_APPROVED_DATE", str(date.today())),
    }

# Module-level references used by build_turtle (set by main before calling)
ABBREV_FILE = Path(__file__).parent.parent / "data" / "samples" / "abbreviations.csv"
FILE_ID = "IT-AbbreviationFile-v1"
APPROVED_DATE = str(date.today())

NAMED_GRAPH = "urn:abbrev:mapping"
BM = "urn:org:metadata:"
XSD = "http://www.w3.org/2001/XMLSchema#"


def _uri(local: str) -> str:
    return f"<{BM}{quote(local, safe='')}>"


def _lit(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _lit_typed(value: str, xsd_type: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"^^<{XSD}{xsd_type}>'


def build_turtle(rows: list[dict]) -> str:
    """Convert CSV rows to Turtle RDF for the abbreviation named graph."""
    buf = io.StringIO()

    buf.write(f"@prefix bm:  <{BM}> .\n")
    buf.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n")
    buf.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n\n")

    # AbbreviationFile node
    file_uri = _uri(FILE_ID)
    buf.write(f"{file_uri} a bm:AbbreviationFile ;\n")
    buf.write(f"    bm:fileVersion {_lit(FILE_ID)} ;\n")
    buf.write(f"    bm:approvedDate {_lit_typed(APPROVED_DATE, 'date')} .\n\n")

    domain_uris: set[str] = set()

    for row in rows:
        short = row["short_name"].strip()
        full = row["full_name"].strip()
        domain = row["domain"].strip()
        definition = row["definition"].strip()

        abbrev_uri = _uri(f"abbrev_{short}")
        term_uri = _uri(f"term_{short}")
        domain_uri = _uri(f"domain_{domain.replace(' ', '_')}")

        # Abbreviation node
        buf.write(f"{abbrev_uri} a bm:Abbreviation ;\n")
        buf.write(f"    bm:shortName {_lit(short)} ;\n")
        buf.write(f"    bm:expandsTo {term_uri} ;\n")
        buf.write(f"    bm:approvedBy {file_uri} .\n\n")

        # BusinessTerm node
        buf.write(f"{term_uri} a bm:BusinessTerm ;\n")
        buf.write(f"    bm:fullName {_lit(full)} ;\n")
        buf.write(f"    bm:definition {_lit(definition)} ;\n")
        buf.write(f"    bm:belongsToDomain {domain_uri} .\n\n")

        # BusinessDomain node (emit once per domain)
        if domain_uri not in domain_uris:
            domain_uris.add(domain_uri)
            buf.write(f"{domain_uri} a bm:BusinessDomain ;\n")
            buf.write(f"    rdfs:label {_lit(domain)} .\n\n")

    return buf.getvalue()


def load_to_stardog(turtle: str, named_graph: str, cfg: dict) -> None:
    """POST Turtle data into Stardog under the given named graph."""
    url = f"{cfg['endpoint']}/{cfg['db']}/data"
    params = {"graph-uri": named_graph}
    headers = {"Content-Type": "text/turtle"}
    resp = requests.post(
        url,
        params=params,
        data=turtle.encode("utf-8"),
        headers=headers,
        auth=(cfg["user"], cfg["password"]),
        timeout=30,
    )
    resp.raise_for_status()
    print(f"Loaded {len(turtle)} bytes into <{named_graph}>  HTTP {resp.status_code}")


def main() -> None:
    cfg = _config()
    abbrev_file = cfg["abbrev_file"]
    if not abbrev_file.exists():
        print(f"ERROR: Abbreviation file not found: {abbrev_file}", file=sys.stderr)
        sys.exit(1)

    # Update module-level vars used by build_turtle
    global FILE_ID, APPROVED_DATE
    FILE_ID = cfg["file_id"]
    APPROVED_DATE = cfg["approved_date"]

    with abbrev_file.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    print(f"Read {len(rows)} abbreviations from {abbrev_file}")
    turtle = build_turtle(rows)
    load_to_stardog(turtle, NAMED_GRAPH, cfg)
    print("Done.")


if __name__ == "__main__":
    main()
