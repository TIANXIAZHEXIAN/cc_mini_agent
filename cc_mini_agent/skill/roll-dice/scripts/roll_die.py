"""Roll one die with a configurable number of sides."""

from __future__ import annotations

import argparse
import random


def main() -> None:
    parser = argparse.ArgumentParser(description="Roll one die.")
    parser.add_argument("sides", type=int, help="Number of sides on the die.")
    args = parser.parse_args()

    if args.sides < 1:
        raise SystemExit("sides must be greater than zero")

    print(random.randint(1, args.sides))


if __name__ == "__main__":
    main()
