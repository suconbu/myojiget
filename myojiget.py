#!/usr/bin/env python3

import os
import re
import sys
import json
import requests
import argparse
from bs4 import BeautifulSoup

def get_textcontent(uri: str) -> str:
    text = ""
    try:
        if uri.startswith("file:"):
            with open(uri[5:], "r", encoding="utf-8") as f:
                text = f.read()
        else:
            response = requests.get(uri)
            response.encoding = response.apparent_encoding
            text = response.text
    except:
        pass
    return text

def get_bsoup(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, "html.parser")

class Setting(object):
    myoji_uri_base = "https://myoji-yurai.net/searchResult.htm?myojiKanji={myoji}"
    origin_not_registered = "の解説はまだ登録されていません。"

def get_myoji_from_html(text:str) -> dict:
    """
    指定された名字詳細ページ文字列の内容から名字情報を取得します。
    
    Args:
        text (str): 名字詳細ページのHTML文字列

    Returns:
        dict: 名字情報
    """
    result = {}
    bsPage = get_bsoup(text)
    bsPosts = bsPage.select("div#content > div.post")

    # 【名字】山田
    #         ~~~~
    result["myojiKanji"] = bsPosts[0].select_one("h1.title").get_text()[4:]

    # 【読み】やまだ,やまた,ようだ,やだ
    #         ~~~~~~~~~~~~~~~~~~~~~~~~~
    result["myojiYomis"] = bsPosts[0].select_one("p.meta").get_text()[4:].split(",")

    if len(result["myojiYomis"]) == 0:
        return {}

    bsRankAndCount = bsPosts[1].select_one("p").get_text()

    # 【全国順位】 12位
    #              ~~
    match = re.search('(\d+)位', bsRankAndCount)
    if not match:
        return {}
    result["rankInCountry"] = int(match.group(1))

    # 【全国人数】 およそ814,000人
    #                    ~~~~~~~
    match = re.search('([\d,]+)人', bsRankAndCount)
    if not match:
        return {}
    result["countInCountry"] = int(match.group(1).replace(",", ""))

    # 名字の由来
    bsMyojiOrigin = bsPosts[2].select_one("div.box > div.myojiComments")
    if bsMyojiOrigin.a:
        result["myojiOriginDetailUri"] = bsMyojiOrigin.a["href"]
        bsMyojiOrigin.a.decompose()
    for br in bsMyojiOrigin.select("br"):
        br.replace_with("\n")
    myoji_origin = bsMyojiOrigin.get_text().strip()
    if Setting.origin_not_registered in myoji_origin:
        result["myojiOrigin"] = None
    else:
        result["myojiOrigin"] = myoji_origin

    return result

def get_myoji(myoji:str) -> dict:
    """
    指定された名字に該当する名字情報を取得します。
    該当する名字情報がない時は空の辞書を返します。

    Args:
        myoji (str): 名字文字列

    Returns:
        dict: 名字情報

    名字情報:
        myoujiKanji: 名字漢字
        myoujiYomis: 名字よみのリスト
        rankInCountry: 全国人数順位
        countInCountry: 全国人数
        myojiOrigin: 名字由来文(複数行テキスト)
        myojiOriginDetailUri: 名字由来詳細ページのURI
    """
    result = None
    uri = Setting.myoji_uri_base.replace("{myoji}", myoji)
    text = get_textcontent(uri)
    return get_myoji_from_html(text)

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("myoji", nargs="?")
    args = ap.parse_args(argv[1:])

    if not args.myoji:
        return

    myoji_result = get_myoji(args.myoji)
    if myoji_result:
        print(json.dumps(myoji_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main(sys.argv)
