#!/usr/bin/env python3
import json
from pathlib import Path
import sys

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "LICENSE",
    "README.md",
    "CITATION.cff",
    "codemeta.json",
    ".zenodo.json",
    "ro-crate-metadata.json",
    "scripts/generate_ro_crate.py",
    "scripts/validate_metadata.py",
]

EXPECTED_ORCID = "0000-0001-8260-231X"
EXPECTED_TITLE = "CoastSat interface.crate generation"
EXPECTED_LICENSE = "Apache-2.0"
ROCRATE_VERSION = "https://w3id.org/ro/crate/1.1"


def normalize_license(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("https://spdx.org/licenses/"):
        return value.rsplit("/", 1)[-1]
    return value


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def find_rocrate_entity(graph: list[dict], entity_id: str) -> dict | None:
    for entity in graph:
        if entity.get("@id") == entity_id:
            return entity
    return None


def contains_ellipsis(value: str | None) -> bool:
    return bool(value and "..." in value)


def report(label: str, ok: bool, details: str | None = None) -> bool:
    status = "✅" if ok else "❌"
    if ok:
        print(f"{status} {label}")
    else:
        suffix = f": {details}" if details else ""
        print(f"{status} {label}{suffix}")
    return ok


def main() -> int:
    failures = 0

    missing = [path for path in REQUIRED_FILES if not (REPO_ROOT / path).exists()]
    if not report("Required files present", not missing, ", ".join(missing) if missing else None):
        failures += 1

    try:
        codemeta = load_json(REPO_ROOT / "codemeta.json")
        zenodo = load_json(REPO_ROOT / ".zenodo.json")
        rocrate = load_json(REPO_ROOT / "ro-crate-metadata.json")
        report("JSON files parse", True)
    except Exception as exc:
        report("JSON files parse", False, str(exc))
        return 1

    try:
        citation = load_yaml(REPO_ROOT / "CITATION.cff")
        report("CITATION.cff parses", True)
    except Exception as exc:
        report("CITATION.cff parses", False, str(exc))
        return 1

    graph = rocrate.get("@graph", [])
    root_dataset = find_rocrate_entity(graph, "./")
    metadata_descriptor = find_rocrate_entity(graph, "ro-crate-metadata.json")

    if not report("RO-Crate root dataset exists", root_dataset is not None):
        failures += 1
    else:
        report("RO-Crate metadata descriptor exists", metadata_descriptor is not None)
        if metadata_descriptor is None:
            failures += 1
        else:
            conforms_to = metadata_descriptor.get("conformsTo", {})
            conforms_id = conforms_to.get("@id") if isinstance(conforms_to, dict) else None
            if not report("RO-Crate conformsTo 1.1", conforms_id == ROCRATE_VERSION, conforms_id):
                failures += 1

    titles = {
        "citation": citation.get("title"),
        "codemeta": codemeta.get("name"),
        "zenodo": zenodo.get("title"),
        "rocrate": root_dataset.get("name") if root_dataset else None,
    }
    unique_titles = {value for value in titles.values() if value}
    if not report(
        "Title matches across metadata",
        len(unique_titles) == 1 and EXPECTED_TITLE in unique_titles,
        str(titles),
    ):
        failures += 1

    licenses = {
        "citation": normalize_license(citation.get("license")),
        "codemeta": normalize_license(codemeta.get("license")),
        "zenodo": normalize_license(zenodo.get("license")),
        "rocrate": normalize_license(root_dataset.get("license") if root_dataset else None),
    }
    unique_licenses = {value for value in licenses.values() if value}
    if not report(
        "License matches across metadata",
        len(unique_licenses) == 1 and EXPECTED_LICENSE in unique_licenses,
        str(licenses),
    ):
        failures += 1

    citation_orcid = None
    if citation.get("authors"):
        citation_orcid = citation["authors"][0].get("orcid", "").replace("https://orcid.org/", "")
    codemeta_orcid = None
    if codemeta.get("author"):
        codemeta_orcid = codemeta["author"][0].get("@id", "").replace("https://orcid.org/", "")
    zenodo_orcid = None
    if zenodo.get("creators"):
        zenodo_orcid = zenodo["creators"][0].get("orcid")
    rocrate_orcid = None
    if graph:
        for entity in graph:
            if entity.get("@id", "").endswith(EXPECTED_ORCID):
                rocrate_orcid = EXPECTED_ORCID
                break

    orcid_values = {
        "citation": citation_orcid,
        "codemeta": codemeta_orcid,
        "zenodo": zenodo_orcid,
        "rocrate": rocrate_orcid,
    }
    unique_orcids = {value for value in orcid_values.values() if value}
    if not report(
        "ORCID matches across metadata",
        len(unique_orcids) == 1 and EXPECTED_ORCID in unique_orcids,
        str(orcid_values),
    ):
        failures += 1

    descriptions = {
        "citation": citation.get("abstract"),
        "codemeta": codemeta.get("description"),
        "zenodo": zenodo.get("description"),
        "rocrate": root_dataset.get("description") if root_dataset else None,
    }
    ellipsis_found = {key: value for key, value in descriptions.items() if contains_ellipsis(value)}
    if not report("Descriptions are not truncated", not ellipsis_found, str(ellipsis_found)):
        failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
