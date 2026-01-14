# CoastSat interface.crate generation [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18250232.svg)](https://doi.org/10.5281/zenodo.18250232)


This repository implements the generation of a LivePublication `interface.crate` for the CoastSat case study (Chapter 6). It produces RO-Crate metadata that describes the experiment infrastructure outputs required by the LivePublication interface, contributing tooling that constructs and validates the crate used as the interface object between computational infrastructure and live publications.


## What it generates

- `interface.crate/` — a LivePublication interface RO-Crate for the CoastSat case study

## Quick start

Prerequisites:
- Conda (recommended) and Python 3.10
- A GitHub Personal Access Token with Gist permissions (`GITHUB_TOKEN`)

```bash
conda env create -f environment.yaml
conda activate coastsat_stencila_env
export GITHUB_TOKEN=your_token_here
python LP_Crate/interface_crate.py --coastsat-dir CoastSat --output-dir interface.crate
```

## Outputs

- The main crate is written to `interface.crate/` (including its `ro-crate-metadata.json`).
- Notebook-level crates are placed under `interface.crate/notebooks/`.
- Summary outputs are written to `LP_Crate/summaries/` when the summary scripts are run.

## How to cite

TODO: add the Zenodo DOI after the first archival release.

## Related artefacts

- Upstream CoastSat repository: https://github.com/UoA-eResearch/CoastSat

## License

Apache-2.0. See `LICENSE`.

## Metadata validation

```bash
make validate-metadata
```

## RO-Crate regeneration

```bash
python scripts/generate_ro_crate.py
```
