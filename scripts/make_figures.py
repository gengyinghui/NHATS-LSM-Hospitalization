from __future__ import annotations

from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.utils import binomial_ci, parse_or_ci, clean_traj_label


def _save(fig, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f'{name}.png', dpi=200)
    plt.close(fig)


def main_fig1_distribution(root: Path, out: Path) -> None:
    groups = ['Q1 low-declining', 'Q2 moderate-stable', 'Q3 high-declining', 'Q4 high-stable']
    n = [717, 738, 721, 731]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(groups, n)
    for i, v in enumerate(n):
        ax.text(i, v + 8, str(v), ha='center', va='bottom')
    ax.set_ylabel('Number of participants')
    ax.set_title('Distribution of life-space mobility trajectory groups')
    ax.set_ylim(0, max(n) * 1.15)
    ax.tick_params(axis='x', rotation=20)
    _save(fig, out, 'main_Figure_1_distribution_trajectory_groups')


def main_fig2_annual_rates(root: Path, out: Path) -> None:
    supp = pd.ExcelFile(root / 'data' / 'derived' / 'supplement_tables_clean.xlsx')
    overall = pd.read_excel(supp, 'eTable S3 - Year overall')
    stacked = pd.read_excel(supp, 'eTable S4 - Year×traj stacked')

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    ax = axes[0]
    # approximate CI from text columns where needed; figure emphasizes annual pattern.
    ax.plot(overall['Year'], overall['Rate(%)'], marker='o')
    ax.set_title('A. Overall annual hospitalization rate')
    ax.set_xlabel('Year')
    ax.set_ylabel('Hospitalization rate (%)')
    ax.set_xticks(overall['Year'])
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)

    ax = axes[1]
    pivot = stacked.pivot(index='fyear', columns='traj', values='Rate_pct')
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], marker='o', label=col)
    ax.set_title('B. Annual crude rates by trajectory')
    ax.set_xlabel('Year')
    ax.set_ylabel('Hospitalization rate (%)')
    ax.set_xticks(sorted(stacked['fyear'].unique()))
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax.legend(fontsize=8)
    _save(fig, out, 'main_Figure_2_annual_hospitalization_rates')


def main_fig3_adjusted_associations(root: Path, out: Path) -> None:
    main = pd.ExcelFile(root / 'data' / 'derived' / 'clean_tables_for_main.xlsx')
    dfs = [('A. Stacked analysis', pd.read_excel(main, 'Table 2 - Rehosp (stacked)')),
           ('B. First-window sensitivity', pd.read_excel(main, 'Table 2 - Rehosp (first)'))]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharex=True)
    for ax, (title, df) in zip(axes, dfs):
        parsed = df['aOR (95% CI)'].apply(parse_or_ci)
        df[['OR','LCL','UCL']] = pd.DataFrame(parsed.tolist(), index=df.index)
        df['label'] = df['Trajectory'].apply(clean_traj_label)
        plot_df = df.iloc[1:].copy()
        y = np.arange(len(plot_df))[::-1]
        xerr = np.vstack([plot_df['OR'] - plot_df['LCL'], plot_df['UCL'] - plot_df['OR']])
        ax.errorbar(plot_df['OR'], y, xerr=xerr, fmt='o', capsize=3)
        ax.axvline(1, linestyle='--')
        ax.set_yticks(y)
        ax.set_yticklabels(plot_df['label'])
        ax.set_xscale('log')
        ax.set_xlabel('Adjusted odds ratio vs Q1 (95% CI)')
        ax.set_title(title)
        ax.grid(True, axis='x', linestyle='--', alpha=0.4)
    _save(fig, out, 'main_Figure_3_adjusted_associations')


def supp_fig1_flow(root: Path, out: Path) -> None:
    boxes = [
        'NHATS public-use analytic file\n2015–2023\n6,558 unique participants\n29,413 respondent-years',
        'Balanced-panel trajectory cohort\nInterviewed across all nine annual waves\n2,907 participants',
        'K-means trajectory assignment\nQ1 low-declining: n=717\nQ2 moderate-stable: n=738\nQ3 high-declining: n=721\nQ4 high-stable: n=731',
        'Hospitalization analysis\n26,163 respondent-years\nwith assigned trajectories and non-missing\n12-month hospitalization status'
    ]
    fig, ax = plt.subplots(figsize=(9, 8))
    ax.axis('off')
    ys = [0.86, 0.62, 0.38, 0.14]
    for y, text in zip(ys, boxes):
        ax.text(0.5, y, text, ha='center', va='center', fontsize=11,
                bbox=dict(boxstyle='round,pad=0.5', fc='white', ec='black'))
    for y1, y2 in zip(ys[:-1], ys[1:]):
        ax.annotate('', xy=(0.5, y2+0.09), xytext=(0.5, y1-0.09),
                    arrowprops=dict(arrowstyle='->', lw=1.5))
    ax.set_title('Participant-flow diagram and trajectory assignment')
    _save(fig, out, 'Supplementary_Figure_S1_participant_flow')


def supp_fig2_overall_by_year(root: Path, out: Path) -> None:
    df = pd.read_excel(root / 'data' / 'derived' / 'supplement_tables_clean.xlsx', sheet_name='eTable S3 - Year overall')
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df['Year'].astype(str), df['Rate(%)'])
    for i, v in enumerate(df['Rate(%)']):
        ax.text(i, v + 0.5, f'{v:.1f}', ha='center')
    ax.set_ylabel('Hospitalization rate (%)')
    ax.set_xlabel('Year')
    ax.set_title('Overall hospitalization (12-month) rate by year, 2015–2023')
    ax.set_ylim(0, max(df['Rate(%)']) + 6)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    _save(fig, out, 'Supplementary_Figure_S2_overall_by_year')


def supp_fig3_by_traj(root: Path, out: Path) -> None:
    df = pd.read_excel(root / 'data' / 'derived' / 'supplement_tables_clean.xlsx', sheet_name='eTable S1 - Rates stacked')
    lo, hi = binomial_ci(df['Events'], df['N'])
    df['lo'], df['hi'] = lo, hi
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(df))
    ax.bar(x, df['Rate_pct'])
    ax.errorbar(x, df['Rate_pct'], yerr=[df['Rate_pct']-df['lo'], df['hi']-df['Rate_pct']], fmt='none', capsize=4)
    for i, (rate, n) in enumerate(zip(df['Rate_pct'], df['N'])):
        ax.text(i, rate + 0.8, f'{rate:.1f}', ha='center')
        ax.text(i, 0.8, f'n={int(n):,}', ha='center', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(df['traj'], rotation=15)
    ax.set_ylabel('Hospitalization rate (%)')
    ax.set_title('Hospitalization (12-month) by life-space trajectory')
    ax.set_ylim(0, max(df['hi']) + 6)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    _save(fig, out, 'Supplementary_Figure_S3_by_trajectory')


def supp_fig4_stacked_faceted(root: Path, out: Path) -> None:
    """Generate the year-by-trajectory stacked summary figure.

    A compact line figure is used for reproducibility and stable rendering across
    systems. The manuscript/supplement may display a faceted version, but this
    figure uses the same year-by-trajectory input table and reproduces the same
    rate pattern.
    """
    df = pd.read_excel(root / 'data' / 'derived' / 'supplement_tables_clean.xlsx', sheet_name='eTable S4 - Year×traj stacked')
    fig, ax = plt.subplots(figsize=(9, 5))
    for traj, sub in df.groupby('traj', sort=False):
        ax.plot(sub['fyear'], sub['Rate_pct'], marker='o', label=traj)
    ax.set_ylabel('Hospitalization rate (%)')
    ax.set_xlabel('Year')
    ax.set_title('Stacked specification: hospitalization by year and trajectory')
    ax.set_xticks(sorted(df['fyear'].unique()))
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylim(0, 35)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax.legend(fontsize=8)
    _save(fig, out, 'Supplementary_Figure_S4_stacked_year_by_trajectory')

def supp_fig5_first_window(root: Path, out: Path) -> None:
    df = pd.read_excel(root / 'data' / 'derived' / 'supplement_tables_clean.xlsx', sheet_name='eTable S1 - Rates first')
    lo, hi = binomial_ci(df['Events'], df['N'])
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(df))
    ax.bar(x, df['Rate_pct'])
    ax.errorbar(x, df['Rate_pct'], yerr=[df['Rate_pct']-lo, hi-df['Rate_pct']], fmt='none', capsize=4)
    for i, (rate, n) in enumerate(zip(df['Rate_pct'], df['N'])):
        ax.text(i, rate + 0.7, f'{rate:.1f}', ha='center')
        ax.text(i, 0.8, f'n={int(n):,}', ha='center', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(df['traj'], rotation=15)
    ax.set_ylabel('Hospitalization rate (%)')
    ax.set_title('First-window hospitalization by life-space trajectory')
    ax.set_ylim(0, max(hi) + 6)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    _save(fig, out, 'Supplementary_Figure_S5_first_window_by_trajectory')


def supp_fig6_7_sensitivity(root: Path, out: Path) -> None:
    main = pd.ExcelFile(root / 'data' / 'derived' / 'clean_tables_for_main.xlsx')
    for sheet, name, title in [
        ('Table 2 - Rehosp (first)', 'Supplementary_Figure_S6_first_window_adjusted_estimates', 'First-window adjusted estimates'),
        ('Table 2 - Rehosp (stacked)', 'Supplementary_Figure_S7_stacked_adjusted_estimates', 'Stacked adjusted estimates')]:
        df = pd.read_excel(main, sheet_name=sheet)
        parsed = df['aOR (95% CI)'].apply(parse_or_ci)
        df[['OR','LCL','UCL']] = pd.DataFrame(parsed.tolist(), index=df.index)
        df = df.iloc[1:].copy()
        labels = df['Trajectory'].apply(clean_traj_label)
        y = np.arange(len(df))[::-1]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        xerr = np.vstack([df['OR']-df['LCL'], df['UCL']-df['OR']])
        ax.errorbar(df['OR'], y, xerr=xerr, fmt='o', capsize=4)
        ax.axvline(1, linestyle='--')
        ax.set_yticks(y)
        ax.set_yticklabels(labels)
        ax.set_xscale('log')
        ax.set_xlabel('Adjusted odds ratio vs Q1 (95% CI)')
        ax.set_title(title)
        ax.grid(True, axis='x', linestyle='--', alpha=0.4)
        _save(fig, out, name)


def make_figures(root: Path) -> None:
    out = root / 'outputs' / 'figures'
    main_fig1_distribution(root, out)
    main_fig2_annual_rates(root, out)
    main_fig3_adjusted_associations(root, out)
    supp_fig1_flow(root, out)
    supp_fig2_overall_by_year(root, out)
    supp_fig3_by_traj(root, out)
    supp_fig4_stacked_faceted(root, out)
    supp_fig5_first_window(root, out)
    supp_fig6_7_sensitivity(root, out)
    print(f'Figures written to {out}')
