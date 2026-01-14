#!/usr/bin/env python3
from pathlib import Path

from rocrate.rocrate import ROCrate
from rocrate.model.contextentity import ContextEntity

TITLE = "CoastSat interface.crate generation"
DESCRIPTION = (
    "Tooling that generates a LivePublication interface.crate for the CoastSat case study, "
    "producing RO-Crate metadata that describes experiment infrastructure outputs and supports "
    "reproducible live publications."
)
LICENSE = "https://spdx.org/licenses/Apache-2.0"
VERSION = "TODO"
CODE_REPOSITORY = "https://github.com/GusEllerm/CoastSat-interface.crate"
ORCID = "https://orcid.org/0000-0001-8260-231X"


def add_context_file(crate: ROCrate, relative_path: Path) -> ContextEntity:
    entity = ContextEntity(
        crate,
        relative_path.as_posix(),
        properties={"@type": "File", "name": relative_path.name},
    )
    crate.add(entity)
    return entity


def build_crate(crate_root: Path) -> ROCrate:
    crate = ROCrate()

    crate.root_dataset["name"] = TITLE
    crate.root_dataset["description"] = DESCRIPTION
    crate.root_dataset["license"] = LICENSE
    crate.root_dataset["version"] = VERSION

    crate.metadata["conformsTo"] = {"@id": "https://w3id.org/ro/crate/1.1"}

    person = ContextEntity(
        crate,
        ORCID,
        properties={
            "@type": "Person",
            "name": "Augustus Ellerm",
            "givenName": "Augustus",
            "familyName": "Ellerm",
        },
    )
    crate.add(person)

    software = ContextEntity(
        crate,
        "#coastsat-interface-crate-generator",
        properties={
            "@type": "SoftwareSourceCode",
            "name": TITLE,
            "description": DESCRIPTION,
            "codeRepository": CODE_REPOSITORY,
            "license": LICENSE,
            "author": {"@id": ORCID},
        },
    )
    crate.add(software)
    crate.root_dataset["mainEntity"] = {"@id": software.id}

    key_files = [
        Path("README.md"),
        Path("LICENSE"),
        Path("LP_Crate/interface_crate.py"),
        Path("LP_Crate/make_crate.sh"),
        Path("run_computation.sh"),
        Path("environment.yaml"),
        Path("scripts/generate_ro_crate.py"),
        Path("scripts/validate_metadata.py"),
        Path("CITATION.cff"),
        Path("codemeta.json"),
        Path(".zenodo.json"),
    ]

    has_part = []
    for rel_path in key_files:
        if (crate_root / rel_path).exists():
            has_part.append(add_context_file(crate, rel_path))

    if has_part:
        crate.root_dataset["hasPart"] = has_part

    return crate


def main() -> None:
    crate_root = Path(__file__).resolve().parents[1]
    crate = build_crate(crate_root)
    crate.write(crate_root)


if __name__ == "__main__":
    main()
