#!/usr/bin/env python3
"""
ci/validate_ontology.py
────────────────────────
CI step: validates that all .ttl files in the project parse as valid Turtle
and that the core ontology loads without errors.

Requires:  pip install rdflib

Exit codes:
  0 – all files valid
  1 – one or more files failed to parse
"""

import sys
from pathlib import Path

try:
    import rdflib
except ImportError:
    print("ERROR: rdflib is not installed. Run: pip install rdflib", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).parent.parent
TTL_DIRS = [ROOT / "ontology", ROOT / "data" / "samples"]


def validate_file(path: Path) -> bool:
    g = rdflib.Graph()
    try:
        g.parse(str(path), format="turtle")
        triple_count = len(g)
        print(f"  OK  {path.relative_to(ROOT)}  ({triple_count} triples)")
        return True
    except Exception as exc:
        print(f"  FAIL {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
        return False


def main() -> None:
    ttl_files = []
    for directory in TTL_DIRS:
        ttl_files.extend(sorted(directory.glob("**/*.ttl")))

    if not ttl_files:
        print("No .ttl files found — nothing to validate.", file=sys.stderr)
        sys.exit(1)

    print(f"Validating {len(ttl_files)} Turtle file(s)...\n")
    results = [validate_file(f) for f in ttl_files]

    passed = sum(results)
    failed = len(results) - passed
    print(f"\n{passed} passed, {failed} failed.")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
