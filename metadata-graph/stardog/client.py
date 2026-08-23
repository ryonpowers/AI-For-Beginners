"""
stardog/client.py
──────────────────
Thin Python wrapper around the Stardog HTTP API.
Reads connection details exclusively from environment variables.

Environment variables:
  STARDOG_ENDPOINT  – base URL, e.g. http://localhost:5820
  STARDOG_DB        – database name
  STARDOG_USER      – username
  STARDOG_PASSWORD  – password

Usage:
    from stardog.client import StardogClient

    client = StardogClient()
    results = client.sparql_select("SELECT * WHERE { ?s ?p ?o } LIMIT 10")
    client.load_turtle(turtle_str, named_graph="urn:my:graph")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from requests.auth import HTTPBasicAuth


class StardogClient:
    """Minimal Stardog HTTP API client.

    All connection configuration is sourced from environment variables only —
    no credentials are accepted as constructor parameters.
    """

    def __init__(self) -> None:
        self._endpoint = os.environ["STARDOG_ENDPOINT"].rstrip("/")
        self._db = os.environ["STARDOG_DB"]
        self._auth = HTTPBasicAuth(
            os.environ["STARDOG_USER"],
            os.environ["STARDOG_PASSWORD"],
        )

    # ── Helpers ────────────────────────────────────────────────────────────

    def _db_url(self, path: str = "") -> str:
        return f"{self._endpoint}/{self._db}{path}"

    def _check(self, response: requests.Response) -> requests.Response:
        response.raise_for_status()
        return response

    # ── Database management ────────────────────────────────────────────────

    def create_database(self, options: dict[str, Any] | None = None) -> None:
        """Create the configured database if it does not already exist."""
        payload: dict[str, Any] = {"dbname": self._db}
        if options:
            payload["options"] = options
        resp = requests.post(
            f"{self._endpoint}/admin/databases",
            json=payload,
            auth=self._auth,
            timeout=30,
        )
        if resp.status_code == 409:
            print(f"Database '{self._db}' already exists — skipping creation.")
        else:
            self._check(resp)
            print(f"Database '{self._db}' created.")

    def drop_database(self) -> None:
        """Drop the configured database (use with caution)."""
        self._check(
            requests.delete(
                f"{self._endpoint}/admin/databases/{self._db}",
                auth=self._auth,
                timeout=30,
            )
        )
        print(f"Database '{self._db}' dropped.")

    # ── Data loading ───────────────────────────────────────────────────────

    def load_turtle(self, turtle: str, named_graph: str) -> None:
        """POST Turtle RDF data into the given named graph."""
        self._check(
            requests.post(
                self._db_url("/data"),
                params={"graph-uri": named_graph},
                data=turtle.encode("utf-8"),
                headers={"Content-Type": "text/turtle"},
                auth=self._auth,
                timeout=60,
            )
        )
        print(f"Loaded {len(turtle):,} bytes → <{named_graph}>")

    def load_file(self, path: str | Path, named_graph: str) -> None:
        """Read a Turtle file from disk and load it into a named graph."""
        turtle = Path(path).read_text(encoding="utf-8")
        self.load_turtle(turtle, named_graph)

    def clear_graph(self, named_graph: str) -> None:
        """Remove all triples from a named graph."""
        self._check(
            requests.delete(
                self._db_url("/data"),
                params={"graph-uri": named_graph},
                auth=self._auth,
                timeout=30,
            )
        )
        print(f"Cleared <{named_graph}>")

    # ── Querying ───────────────────────────────────────────────────────────

    def sparql_select(
        self,
        query: str,
        bindings: dict[str, str] | None = None,
        reasoning: bool = False,
    ) -> list[dict[str, Any]]:
        """Execute a SPARQL SELECT query and return rows as a list of dicts."""
        params: dict[str, Any] = {"query": query, "reasoning": str(reasoning).lower()}
        if bindings:
            for var, val in bindings.items():
                params[f"${var}"] = val

        resp = self._check(
            requests.get(
                self._db_url("/query"),
                params=params,
                headers={"Accept": "application/sparql-results+json"},
                auth=self._auth,
                timeout=60,
            )
        )
        data = resp.json()
        vars_ = data["results"]["bindings"]
        return [
            {k: v.get("value") for k, v in row.items()}
            for row in vars_
        ]

    def sparql_construct(
        self,
        query: str,
        reasoning: bool = False,
    ) -> str:
        """Execute a SPARQL CONSTRUCT query and return Turtle text."""
        resp = self._check(
            requests.get(
                self._db_url("/query"),
                params={"query": query, "reasoning": str(reasoning).lower()},
                headers={"Accept": "text/turtle"},
                auth=self._auth,
                timeout=60,
            )
        )
        return resp.text

    def sparql_update(self, update: str) -> None:
        """Execute a SPARQL UPDATE statement."""
        self._check(
            requests.post(
                self._db_url("/update"),
                data={"update": update},
                auth=self._auth,
                timeout=60,
            )
        )

    def sparql_from_file(
        self,
        path: str | Path,
        bindings: dict[str, str] | None = None,
        reasoning: bool = False,
    ) -> list[dict[str, Any]]:
        """Load a SPARQL SELECT query from a .sparql file and execute it."""
        query = Path(path).read_text(encoding="utf-8")
        return self.sparql_select(query, bindings=bindings, reasoning=reasoning)

    # ── Reasoning ─────────────────────────────────────────────────────────

    def enable_reasoning(self, reasoning_schema: str = "QL") -> None:
        """Set the reasoning schema on the database (OWL 2 QL by default)."""
        self._check(
            requests.post(
                f"{self._endpoint}/admin/databases/{self._db}/options",
                json={"reasoning.schema": reasoning_schema},
                auth=self._auth,
                timeout=30,
            )
        )
        print(f"Reasoning schema set to {reasoning_schema}")

    # ── Integrity constraints ─────────────────────────────────────────────

    def add_constraints(self, constraints_turtle: str) -> None:
        """Add integrity constraints (IC) to the database."""
        self._check(
            requests.post(
                self._db_url("/icv/add"),
                data=constraints_turtle.encode("utf-8"),
                headers={"Content-Type": "text/turtle"},
                auth=self._auth,
                timeout=30,
            )
        )
        print("Integrity constraints added.")

    def validate_constraints(self) -> bool:
        """Run ICV and return True if the database is valid."""
        resp = self._check(
            requests.get(
                self._db_url("/icv/violations"),
                headers={"Accept": "application/sparql-results+json"},
                auth=self._auth,
                timeout=60,
            )
        )
        violations = resp.json().get("results", {}).get("bindings", [])
        if violations:
            print(f"ICV violations found: {len(violations)}")
            for v in violations:
                print(" ", v)
            return False
        print("No ICV violations — database is valid.")
        return True
