#!/usr/bin/env python3

import os
import sys
import argparse
import myojiget
import unicodedata

def zenlen(s):
    sw = 0
    for c in s:
        cw = unicodedata.east_asian_width(c)
        sw += 2 if (cw == 'F' or cw == 'W' or cw == "A") else 1
    return sw

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    args = ap.parse_args(argv[1:])

    # 例: "上 中 下 x 山 川|河 原"
    rows, cols = args.input.split("x")
    rows = rows.split()
    cols = cols.split()
    rmax = max(zenlen(row) for row in rows)
    print(f" {' ' * rmax} |{'|'.join(map(lambda c: f' {c:^{10 - (zenlen(c) - len(c))}} ', cols))}")
    print(f"-{'-' * rmax}-|{'|'.join(map(lambda c: '------------', cols))}")
    for row in rows:
        counts = []
        print(f" {row:>{rmax - (zenlen(row) - len(row))}}", end="", flush=True)
        for col in cols:
            colsubs = col.split("|")
            count = 0
            for colsub in colsubs:
                myoji = row + colsub
                result = myojiget.get_myoji(myoji)
                count += result['countInCountry'] if 0 < len(result) else 0
            print(f" | {count:>10,d}", end="", flush=True)
        print()

if __name__ == "__main__":
    main(sys.argv)
