# NHATS-LSM-Hospitalization

Reproducible code package for the manuscript:

**Life-space mobility trajectories and 12-month hospitalization among older adults: findings from the National Health and Aging Trends Study, 2015–2023**

## What this repository contains

This repository contains scripts and de-identified derived summary inputs used to regenerate the submitted main and supplementary tables and figures.

The repository does **not** redistribute individual-level NHATS public-use data. NHATS public-use data and documentation should be obtained directly from NHATS or ICPSR/NACDA under the applicable data-use requirements.

## One-click reproduction

Install Python dependencies and run:

```bash
python -m pip install -r requirements.txt
python run_all.py
```

Generated outputs will be written to:

```text
outputs/tables/
outputs/figures/
```

## Repository structure

```text
NHATS-LSM-Hospitalization/
├── data/
│   ├── README.md
│   └── derived/
│       ├── clean_tables_for_main.xlsx
│       ├── supplement_tables_clean.xlsx
│       ├── rehosp_overall_by_year.csv
│       ├── rehosp_by_traj_by_year.csv
│       └── diag_traj_years_per_pid.csv
├── docs/
│   ├── CODEBOOK.md
│   └── DATA_AVAILABILITY.md
├── outputs/
│   ├── figures/
│   └── tables/
├── scripts/
│   ├── make_figures.py
│   ├── make_tables.py
│   ├── utils.py
│   └── RUN_AGG_figs_SAFE.do
├── requirements.txt
├── run_all.py
└── LICENSE
```

## Notes on reproducibility

- `run_all.py` regenerates the main and supplementary tables and figures from the included derived summary inputs.
- Raw NHATS public-use data are not included. Researchers who wish to reproduce the complete individual-level data preparation workflow should obtain NHATS public-use files directly from NHATS/ICPSR/NACDA and follow the variable definitions described in the manuscript and supplementary material.
- The legacy Stata script `scripts/RUN_AGG_figs_SAFE.do` is included for transparency and can be adapted by users who have the required local Stata `.dta` files.

## Citation

If using this code, please cite the associated manuscript once published.
