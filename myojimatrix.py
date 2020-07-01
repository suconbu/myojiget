#!/usr/bin/env python3

import os
import sys
import argparse
import myojiget

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    args = ap.parse_args(argv[1:])

    # 例: "上 中 下 x 山 川|河 原"
    rows, cols = args.input.split("x")
    rows = rows.split()
    cols = cols.split()
    rmax = max(myojiget.zenlen(row) for row in rows)
    cmax = 10
    print(f" {' ' * rmax} |{'|'.join(map(lambda c: f' {c:^{cmax - (myojiget.zenlen(c) - len(c))}} ', cols))}")
    print(f"-{'-' * rmax}-|{'|'.join(map(lambda c: '-' * (cmax + 2), cols))}")
    for row in rows:
        counts = []
        print(f" {row:>{rmax - (myojiget.zenlen(row) - len(row))}}", end="", flush=True)
        for col in cols:
            colsubs = col.split("|")
            try:
                count = 0
                for colsub in colsubs:
                    myoji = row + colsub
                    result = myojiget.get_myoji(myoji)
                    count += result['countInCountry'] if result else 0
                cell = f"{count:>{cmax},d}"
            except Exception as e:
                cell = f"{'-':^{cmax}}"
            print(f" | {cell}", end="", flush=True)
        print()

if __name__ == "__main__":
    main(sys.argv)
