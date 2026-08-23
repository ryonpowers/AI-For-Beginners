"""
ingestion/ingest_hierarchies.py
────────────────────────────────
Loads all six hierarchy Turtle files into Stardog, each into its own named graph.

Environment variables: see stardog/client.py

Optional:
  HIERARCHY_DIR – path to directory containing hierarchy .ttl files
                  (default: data/samples/)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from stardog.client import StardogClient

HIERARCHY_DIR = Path(
    os.environ.get("HIERARCHY_DIR", Path(__file__).parent.parent / "data" / "samples")
)

# Maps filename prefix → Stardog named graph URI
HIERARCHY_GRAPHS: dict[str, str] = {
    "hierarchy_dataproduct": "urn:hierarchy:dataproduct",
    "hierarchy_businessdomain": "urn:hierarchy:businessdomain",
    "hierarchy_customer": "urn:hierarchy:customer",
    "hierarchy_entity": "urn:hierarchy:entity",
    "hierarchy_person": "urn:hierarchy:person",
    "hierarchy_fiscal": "urn:hierarchy:fiscal",
}


def main() -> None:
    client = StardogClient()

    for file_stem, named_graph in HIERARCHY_GRAPHS.items():
        ttl_file = HIERARCHY_DIR / f"{file_stem}.ttl"
        if not ttl_file.exists():
            print(f"WARN: {ttl_file} not found — skipping.", file=sys.stderr)
            continue
        print(f"Loading {ttl_file.name} → <{named_graph}>")
        client.load_file(ttl_file, named_graph)

    print("\nAll hierarchies loaded.")


if __name__ == "__main__":
    main()
