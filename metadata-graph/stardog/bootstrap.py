"""
stardog/bootstrap.py
──────────────────────
Creates and initializes the Stardog database with:
  1. The ontology (named graph <urn:org:metadata:ontology>)
  2. Reasoning schema OWL 2 QL
  3. Integrity constraints

Run this once per environment setup.

Environment variables: see stardog/client.py
"""

import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from stardog.client import StardogClient

ONTOLOGY_FILE = Path(__file__).parent.parent / "ontology" / "business_metadata.ttl"
ONTOLOGY_GRAPH = "urn:org:metadata:ontology"

INTEGRITY_CONSTRAINTS = """
@prefix bm:  <urn:org:metadata:> .
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Every Abbreviation must have a shortName and expand to a BusinessTerm
bm:AbbreviationShape a sh:NodeShape ;
    sh:targetClass bm:Abbreviation ;
    sh:property [ sh:path bm:shortName   ; sh:minCount 1 ; sh:datatype xsd:string ] ;
    sh:property [ sh:path bm:expandsTo   ; sh:minCount 1 ] ;
    sh:property [ sh:path bm:approvedBy  ; sh:minCount 1 ] .

# Every BusinessTerm must have a fullName and belong to a domain
bm:BusinessTermShape a sh:NodeShape ;
    sh:targetClass bm:BusinessTerm ;
    sh:property [ sh:path bm:fullName         ; sh:minCount 1 ; sh:datatype xsd:string ] ;
    sh:property [ sh:path bm:belongsToDomain  ; sh:minCount 1 ] .

# Every Report must have a name and type
bm:ReportShape a sh:NodeShape ;
    sh:targetClass bm:Report ;
    sh:property [ sh:path bm:reportName ; sh:minCount 1 ; sh:datatype xsd:string ] ;
    sh:property [ sh:path bm:reportType ; sh:minCount 1 ; sh:datatype xsd:string ] .
"""


def main() -> None:
    client = StardogClient()

    print("Creating database...")
    client.create_database(options={"reasoning.type": "QL"})

    print("Loading ontology...")
    client.load_file(ONTOLOGY_FILE, ONTOLOGY_GRAPH)

    print("Enabling OWL 2 QL reasoning...")
    client.enable_reasoning("QL")

    print("Adding integrity constraints...")
    client.add_constraints(INTEGRITY_CONSTRAINTS)

    print("Validating constraints...")
    ok = client.validate_constraints()

    if ok:
        print("\nBootstrap complete.")
    else:
        print("\nBootstrap completed with constraint violations — review above.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
