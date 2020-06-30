#!/usr/bin/env python3

import os
import sys
import argparse
import myojiget

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    args = ap.parse_args(argv[1:])
    # args = ap.parse_args(["上 下 x 山 川"])

    rows, cols = args.input.split("x")
    rows = rows.split()
    cols = cols.split()

    print(f"   |{'|'.join(map(lambda c: f' {c:^9} ', cols))}")
    print(f"---|{'|'.join(map(lambda c: '------------', cols))}")
    for row in rows:
        counts = []
        print(f"{row}", end="", flush=True)

        for col in cols:
            myoji = row + col
            result = myojiget.get_myoji(myoji)
            count = result['countInCountry'] if 0 < len(result) else 0
            # counts.append(f"{count:>10,d}")
            print(f" | {count:>10,d}", end="", flush=True)
        print()
        # print(f"{row} | {' | '.join(counts)}")

    # if len(args.col) == 0 or len(args.row) == 0:
    #     print("行と列から作られる名字の人数で表を埋めます。")
    #     print("   |     山     |     川    ")
    #     print("---+------------+-----------")
    #     print("上 | (上山さん) | (上川さん)")
    #     print("下 | (下山さん) | (下川さん)")
    #     print()
    #     print("行・列に使う字を半角空白区切りで入れて下さい。")
    #     row_chars = input("行(縦) : ").split(" ")
    #     col_chars = input("列(横) : ").split(" ")
    #     print(f"row_chars: {row_chars}")
    #     print(f"col_chars: {col_chars}")

if __name__ == "__main__":
    main(sys.argv)
