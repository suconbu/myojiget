#!/usr/bin/env python3

import os
import re
import sys
import json
import requests
import argparse
import unicodedata
from bs4 import BeautifulSoup

class Setting(object):
    cache_dir = f"{os.path.expanduser('~')}/.myojiget_cache"
    myoji_uri_base = "https://myoji-yurai.net/searchResult.htm?myojiKanji={myoji}"
    origin_not_registered = "の解説はまだ登録されていません。"

def zenlen(s):
    sw = 0
    for c in s:
        cw = unicodedata.east_asian_width(c)
        sw += 2 if (cw == 'F' or cw == 'W' or cw == "A") else 1
    return sw

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

def str_to_codepointstr(text:str) -> str:
    return "_".join([str(ord(c)) for c in text])

def get_myojicache_path(myoji:str) -> str:
    return os.path.join(Setting.cache_dir, "myoji", f"myoji_{str_to_codepointstr(myoji)}.json")

def get_myojicache(myoji:str) -> dict:
    try:
        cache_path = get_myojicache_path(myoji)
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)
    except Exception as e:
        pass
    return None

def set_myojicache(myoji:str, result:dict):
    try:
        cache_path = get_myojicache_path(myoji)
        cache_dir = os.path.dirname(cache_path)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        with open(cache_path, "w") as f:
            json.dump(result, f, ensure_ascii=False)
    except Exception as e:
        pass

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

    bsRankAndCount = bsPosts[1].select_one("p").get_text()

    # 【全国順位】 12位
    #              ~~
    # 【全国人数】 およそ814,000人
    #                    ~~~~~~~
    rank_match = re.search('(\d+)位', bsRankAndCount)
    count_match = re.search('([\d,]+)人', bsRankAndCount)
    if not rank_match or not count_match:
        return {}
    result["rankInCountry"] = int(rank_match.group(1))
    result["countInCountry"] = int(count_match.group(1).replace(",", ""))

    # 名字の由来
    bsMyojiOrigin = bsPosts[2].select_one("div.box > div.myojiComments")
    if bsMyojiOrigin.a:
        result["myojiOriginDetailUri"] = bsMyojiOrigin.a["href"]
        bsMyojiOrigin.a.decompose()
    else:
        result['myojiOriginDetailUri'] = None
    for br in bsMyojiOrigin.select("br"):
        br.replace_with("\n")
    myoji_origin = bsMyojiOrigin.get_text().strip()
    if Setting.origin_not_registered in myoji_origin:
        result["myojiOrigin"] = None
    else:
        result["myojiOrigin"] = myoji_origin

    return result

def get_myoji(myoji:str, use_cache:bool=True) -> dict:
    """
    指定された名字に該当する名字情報を取得します。
    該当する名字情報がない時は空の辞書を返します。

    Args:
        myoji (str): 名字文字列
        use_cache (bool): キャッシュ使用有無 (既定値:True)

    Returns:
        dict: 名字情報

    名字情報:
        myojiKanji: 名字漢字
        myojiYomis: 名字よみのリスト
        rankInCountry: 全国人数順位
        countInCountry: 全国人数
        myojiOrigin: 名字由来文(複数行テキスト)
        myojiOriginDetailUri: 名字由来詳細ページのURI
    """
    uri = Setting.myoji_uri_base.replace("{myoji}", myoji)
    try:
        result = get_myojicache(myoji) if use_cache else None
        if result is None:
            text = get_textcontent(uri)
            result = get_myoji_from_html(text)
            if result is not None:
                set_myojicache(myoji, result)
        return result
    except Exception as e:
        return {}

def to_text(myoji:dict) -> str:
    text = f"""\
{myoji['myojiKanji']}さんは全国におよそ「{myoji['countInCountry']:#,}人」います。
人数の多さでは全国第「{myoji['rankInCountry']}位」です。
読み方には「{", ".join(myoji['myojiYomis'])}」などがあります。
"""
    myojiOrigin = myoji['myojiOrigin']
    if myojiOrigin:
        lenmax = max(zenlen(s) for s in myojiOrigin.split("\n"))
        text += f"""
名字の由来解説:
{"-" * lenmax}
{myojiOrigin}
{"-" * lenmax}
"""
    if myoji['myojiOriginDetailUri']:
        text += f"""\
詳しくは {myoji['myojiOriginDetailUri']} をご覧ください。
"""
    return text

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--nocache", action="store_true")
    ap.add_argument("--text", action="store_true")
    ap.add_argument("myoji", nargs="?")
    args = ap.parse_args(argv[1:])

    if not args.myoji:
        return

    myoji_result = get_myoji(args.myoji, not args.nocache)
    if myoji_result:
        if args.text:
            print(to_text(myoji_result))
        else:
            print(json.dumps(myoji_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main(sys.argv)
