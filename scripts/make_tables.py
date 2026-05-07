from __future__ import annotations

from pathlib import Path
import pandas as pd


def make_tables(root: Path) -> None:
    data = root / 'data' / 'derived'
    out = root / 'outputs' / 'tables'
    out.mkdir(parents=True, exist_ok=True)

    main_xlsx = data / 'clean_tables_for_main.xlsx'
    supp_xlsx = data / 'supplement_tables_clean.xlsx'

    # Main manuscript tables
    for sheet, filename in {
        'Table 2 - Rehosp (stacked)': 'main_table_2_stacked.csv',
        'Table 2 - Rehosp (first)': 'main_table_2_first_window_sensitivity.csv',
    }.items():
        pd.read_excel(main_xlsx, sheet_name=sheet).to_csv(out / filename, index=False)

    # Main Table 1 is a single overall survey-weighted estimate used in the manuscript.
    pd.DataFrame([{
        'Trajectory': 'Overall', 'N': 29413, 'Events': 6518,
        'Rate (%)': 24.8, '95% CI': '24.00–25.67'
    }]).to_csv(out / 'main_table_1_overall_hospitalization.csv', index=False)

    # Supplementary tables
    sheet_map = {
        'eTable S1 - Rates first': 'supplementary_table_S5_first_window_rates.csv',
        'eTable S2 - OR by year': 'supplementary_table_S6_annual_aORs_stacked.csv',
        'eTable S3 - Year overall': 'supplementary_table_S7_overall_rate_by_year.csv',
        'eTable S4 - Year×traj stacked': 'supplementary_table_S8_year_by_trajectory_stacked.csv',
        'eTable S5 - Year×traj first': 'supplementary_table_S9_baseline_year_first_window.csv',
        'eTable S6 - QC stacked': 'supplementary_table_S10_QC_stacked.csv',
        'eTable S6 - QC first': 'supplementary_table_S10_QC_first.csv',
    }
    for sheet, filename in sheet_map.items():
        pd.read_excel(supp_xlsx, sheet_name=sheet).to_csv(out / filename, index=False)

    print(f'Tables written to {out}')
