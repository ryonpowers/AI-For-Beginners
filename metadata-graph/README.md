# Enterprise Business Metadata Graph Database

A spec-driven metadata management system using **Stardog** that maps
IT-derived abbreviations and source database columns to business domains,
data products, semantic models (Power BI / SSAS), and organizational reports.

---

## Project Structure

```
metadata-graph/
├── ontology/
│   └── business_metadata.ttl       # OWL/Turtle ontology (all classes + properties)
├── ingestion/
│   ├── ingest_abbreviations.py     # CSV → RDF loader for the IT abbreviation file
│   ├── ingest_source_columns.py    # SQL INFORMATION_SCHEMA → RDF loader
│   └── ingest_report_catalog.py    # Turtle report catalog loader
├── sparql/
│   ├── resolve_column_to_term.sparql      # Resolve abbreviated column → full term
│   ├── data_product_lineage.sparql        # Full lineage: source → product → report
│   ├── reports_by_domain.sparql           # Reports surfacing a given business domain
│   ├── abbreviation_coverage.sparql       # Coverage stats per database
│   ├── column_lineage_construct.sparql    # CONSTRUCT: full lineage sub-graph
│   └── term_to_reports.sparql             # Given a term, find all reports
├── stardog/
│   ├── client.py                   # Python Stardog HTTP API wrapper
│   └── bootstrap.py                # One-time DB creation + ontology load
├── data/
│   └── samples/
│       ├── abbreviations.csv       # Sample IT abbreviation mapping file
│       └── report_catalog.ttl      # Sample report catalog (RDF)
├── ci/
│   └── validate_ontology.py        # CI: Turtle syntax validation (rdflib)
├── requirements.txt
└── README.md
```

---

## Architecture

```
Source DBs (SQL Server)
    └─ INFORMATION_SCHEMA ──► SourceColumn nodes  (named graph: urn:source:columns)
                                   │
                         bm:usesAbbreviation
                                   │
IT Abbreviation File (CSV) ──────► Abbreviation ──► BusinessTerm ──► BusinessDomain
                                                         (named graph: urn:abbrev:mapping)
                                   │
                         bm:derivedFrom / bm:mappedToTerm
                                   │
                           DataProductColumn ──► DataProduct
                                                     │
                                           bm:exposedVia
                                                     │
                                           SemanticModel  (Power BI Dataset / SSAS)
                                                     │
                                           bm:consumedBy
                                                     │
                                               Report ──► ServiceOrganization
                                        (named graph: urn:reports:catalog)
```

### Named Graphs

| Graph URI | Contents |
|---|---|
| `urn:org:metadata:ontology` | OWL ontology (classes + properties) |
| `urn:abbrev:mapping` | IT abbreviation → business term mappings |
| `urn:source:columns` | Source DB / schema / table / column metadata |
| `urn:dataproduct:core` | Data product definitions and column mappings |
| `urn:semantic:models` | Semantic model (Power BI / SSAS) catalog |
| `urn:reports:catalog` | Report catalog and org distribution |
| `urn:lineage:full` | Materialized lineage (CONSTRUCT output) |

---

## Prerequisites

- Python 3.11+
- Stardog 8+ running and accessible
- ODBC driver for SQL Server (for `ingest_source_columns.py`)
- `pip install -r requirements.txt`

---

## Environment Variables

Set these before running any script. **Never hardcode credentials.**

```bash
export STARDOG_ENDPOINT="http://localhost:5820"
export STARDOG_DB="business_metadata"
export STARDOG_USER="admin"
export STARDOG_PASSWORD="<your-password>"

# For SQL Server ingestion
export SQL_CONNECTION="DRIVER={ODBC Driver 18 for SQL Server};SERVER=myserver;DATABASE=master;UID=sa;******"
export SQL_DATABASES="SalesDB,FinanceDB"   # optional: comma-separated list

# Optional overrides
export ABBREV_FILE="data/samples/abbreviations.csv"
export ABBREV_FILE_ID="IT-AbbreviationFile-v2"
export ABBREV_APPROVED_DATE="2024-06-01"
```

---

## Quick Start

### 1. Bootstrap the database

```bash
python stardog/bootstrap.py
```

Creates the Stardog database, loads the ontology, enables OWL 2 QL reasoning,
and registers integrity constraints.

### 2. Load abbreviation mapping

```bash
python ingestion/ingest_abbreviations.py
```

### 3. Load source column metadata

```bash
python ingestion/ingest_source_columns.py
```

### 4. Load report catalog

```bash
python ingestion/ingest_report_catalog.py
```

### 5. Run SPARQL queries

```bash
# Resolve an abbreviated column name to its business term
stardog query $STARDOG_DB sparql/resolve_column_to_term.sparql \
  --bind "columnName=cust_id"

# Find all reports surfacing Finance domain data
stardog query $STARDOG_DB sparql/reports_by_domain.sparql \
  --bind "domainLabel=Finance"

# Generate full lineage graph
stardog query $STARDOG_DB sparql/column_lineage_construct.sparql \
  --output-format turtle > lineage_output.ttl
```

---

## CI Validation

The CI pipeline validates all Turtle files for syntax correctness:

```bash
python ci/validate_ontology.py
```

This step must pass before any merge to main.

---

## Roles and Governance

| Role | Responsibility |
|---|---|
| **IT** | Maintains `abbreviations.csv`, manages Stardog instance, approves ontology changes |
| **Business** | Owns `report_catalog.ttl`, defines data product specs, signs off on abbreviation file |
| **Engineering** | Develops ingestion scripts, SPARQL queries, and the Stardog client layer |

Every term in the graph traces back to:
1. An approved abbreviation file (`bm:approvedBy` → `bm:AbbreviationFile`)
2. A data product owner (`bm:owner` property)
3. A named graph with a known load date

---

## Adding a New Business Domain

1. Add abbreviations for the domain to `data/samples/abbreviations.csv`
2. Add a `BusinessDomain` node in the ontology or a new data file
3. Create a data product column mapping Turtle file under `data/`
4. Run `ingest_abbreviations.py` to reload `urn:abbrev:mapping`
5. Run `ci/validate_ontology.py` to confirm no syntax errors
6. Commit all `.ttl` and `.sparql` files to version control
