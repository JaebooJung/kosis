# -*- coding: utf-8 -*-

import json
from string import Template

import requests

from .config import get_apikey

dict_wv_code = {
    "MT_ZTITLE": "국내통계 주제별",
    "MT_OTITLE": "국내통계 기관별",
    "MT_GTITLE01": "지방지표 주제별",
    "MT_GTITLE02": "지방지표 지역별",
    "MT_GTITLE03": "지방지표 테마별",
    "MT_CHOSUN_TITLE": "광복이전 통계",
    "MT_HANKUK_TITLE": "한국통계연감",
    "MT_STOP_TITLE": "작성중지통계",
    "MT_RTITLE": "국제통계",
    "MT_BUKHAN": "북한통계",
    "MT_TM1_TITLE": "대상별 통계",
    "MT_TM2_TITLE": "이슈별 통계",
    "MT_ETITLE": "영문통계"
}

category2wv_code = {
    "topic": "MT_ZTITLE",
    "org": "MT_OTITLE",
    "local_topic": "MT_GTITLE01",
    "local_org": "MT_GTITLE02",
    "local_theme": "MT_GTITLE03",
    "chosun": "MT_CHOSUN_TITLE",
    "yearbook": "MT_HANKUK_TITLE",
    "stopped": "MT_STOP_TITLE",
    "global": "MT_RTITLE",
    "north": "MT_BUKHAN",
    "age": "MT_TM1_TITLE",
    "issue": "MT_TM2_TITLE",
    "english": "MT_ETITLE",
}


def print_category():
    len_command = max(*[len(k) for k in category2wv_code.keys()])
    len_text = max(*[len(dict_wv_code.get(v)) for v in category2wv_code.values()])
    format_str = Template(" {:$l1}: {:$l2}").substitute(l1=len_command + 1, l2=len_text)
    for k, v in category2wv_code.items():
        print(format_str.format(k, dict_wv_code.get(v)))


def fetch_nodes(category, parent_list_id=None):
    wv_code = category2wv_code[category]

    url = "http://kosis.kr/openapi/statisticsList.do"
    params = {
        "format": "json",
        "jsonVD": "Y",
        "apiKey": get_apikey(),
        "method": "getList",
        "vwCd": wv_code,
        "parentListId": parent_list_id
    }
    res = requests.get(url, params=params)
    try:
        all_data = json.loads(res.content.decode("utf-8"))
    except Exception as e_:
        all_data = []
    data = []
    for d in all_data:
        if "LIST_NM" in d:
            data.append({"type": "list", "list_name": d["LIST_NM"], "list_id": d["LIST_ID"]})
        if "TBL_NM" in d:
            data.append({"type": "table", "table_name": d["TBL_NM"], "org_id": d["ORG_ID"], "table_id": d["TBL_ID"]})

    return data


def fetch_subnodes(category, parent_list_id=None):
    print("parent_list_id =", parent_list_id)
    pre_nodes = fetch_nodes(category, parent_list_id)
    nodes = []
    for n in pre_nodes:
        if n["type"] == "list":
            n["children"] = fetch_subnodes(category, n["list_id"])
        nodes.append(n)
    return nodes


def fetch_tree(category):
    fetch_subnodes(category)
