from __future__ import annotations

from pathlib import Path

from scripts.make_tables import make_tables
from scripts.make_figures import make_figures


def main() -> None:
    root = Path(__file__).resolve().parent
    make_tables(root)
    make_figures(root)
    print('\nDone. Reproducible outputs are available in:')
    print(f'  {root / "outputs" / "tables"}')
    print(f'  {root / "outputs" / "figures"}')


if __name__ == '__main__':
    main()
