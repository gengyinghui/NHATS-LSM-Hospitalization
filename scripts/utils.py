from __future__ import annotations

import re
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def parse_or_ci(text: str) -> Tuple[float, float, float]:
    """Parse strings like '0.86 (0.79, 0.94)' or return nan for ref."""
    if not isinstance(text, str) or 'ref' in text.lower():
        return (1.0, np.nan, np.nan)
    nums = [float(x) for x in re.findall(r"\d+\.\d+|\d+", text)]
    if len(nums) >= 3:
        return nums[0], nums[1], nums[2]
    raise ValueError(f"Cannot parse OR/CI from: {text!r}")


def binomial_ci(events: pd.Series, n: pd.Series) -> tuple[pd.Series, pd.Series]:
    rate = events / n
    se = np.sqrt(rate * (1 - rate) / n)
    lo = (rate - 1.96 * se).clip(lower=0)
    hi = (rate + 1.96 * se).clip(upper=1)
    return lo * 100, hi * 100


def clean_traj_label(label: str) -> str:
    if pd.isna(label):
        return ''
    s = str(label)
    s = s.replace('Q1 (lowest)', 'Q1 low-declining')
    s = s.replace('Q2', 'Q2 moderate-stable')
    s = s.replace('Q3', 'Q3 high-declining')
    s = s.replace('Q4 (highest)', 'Q4 high-stable')
    return s
