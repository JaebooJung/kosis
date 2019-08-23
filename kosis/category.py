# -*- coding: utf-8 -*-

import datetime as dt
import json
import os.path
from string import Template

import requests

from .config import get_apikey

__all__ = [
    "print_category",
    "fetch_tree",
    "get_tree",
    "search_tree",
    "get_tables",
    "search_tables",
]

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


def fetch_nodes(category, parent_list_id=None, parent_name=None):
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
            data.append({
                "category": category,
                "type": "list",
                "name": d["LIST_NM"],
                "acc_name": d["LIST_NM"] if parent_name is None else parent_name + "/" + d["LIST_NM"],
                "acc_id": d["LIST_ID"] if parent_list_id is None else parent_list_id + "/" + d["LIST_ID"],
                "id": d["LIST_ID"]
            })
        if "TBL_NM" in d:
            data.append({
                "category": category,
                "type": "table",
                "name": d["TBL_NM"],
                "list_names": parent_name,
                "list_ids": parent_name,
                "id": d["TBL_ID"],
                "org_id": d["ORG_ID"],
            })

    return data


def fetch_subnodes(category, parent_list_id=None, parent_name=None, max_level=1e9, level=0):
    level += 1
    if level > max_level:
        return []
    if parent_list_id is not None:
        print("parent_list_id =", parent_list_id)
    first_nodes = fetch_nodes(category, parent_list_id, parent_name)
    nodes = []
    for n in first_nodes:
        if n["type"] == "list":
            n["children"] = fetch_subnodes(category, n["id"], n["acc_name"], max_level=max_level, level=level)
        nodes.append(n)
    return nodes


def fetch_tree(category=None, max_level=1e9):
    json_path = os.path.join(os.path.dirname(__file__), category + ".json")
    if not os.path.exists(json_path):
        with open(json_path, "w") as json_file:
            json_file.write("{}")
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    nodes = fetch_subnodes(category, max_level=max_level)
    json_data[category] = nodes
    json_data[category + "-timestamp"] = dt.datetime.now().isoformat()
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)


def get_tree(category):
    json_path = os.path.join(os.path.dirname(__file__), category + ".json")
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    return json_data


def node_copy(node):
    keys = ["category", "type", "name", "id", "org_id", "list_names", "list_ids"]
    return {k: v for k, v in node.items() if k in keys}


def search_node(result, nodes, key):
    for n in nodes:
        if (n["type"] == "table") and (n["name"].strip().find(key) >= 0):
            n_copy = node_copy(n)
            result.append(n_copy)
        if ("list_names" in n) and (n["list_names"].strip().find(key) >= 0):
            n_copy = node_copy(n)
            result.append(n_copy)
        if "children" in n:
            result = search_node(result, n["children"], key)
    return result


def search_tree(category, key):
    json_data = get_tree(category)
    nodes = json_data[category]
    result = []
    result = search_node(result, nodes, key)
    return result


def search_tablenode(result, nodes):
    for n in nodes:
        if n["type"] == "table":
            n_copy = node_copy(n)
            result.append(n_copy)
        if "children" in n:
            result = search_tablenode(result, n["children"])
    return result


def get_tables(category):
    json_data = get_tree(category)
    nodes = json_data[category]
    result = []
    result = search_tablenode(result, nodes)
    return result


def search_tables(category, key, search_listname=False):
    tables = get_tables(category)
    result = []
    for t in tables:
        if t["name"].strip().find(key) >= 0:
            result.append(t)
        if search_listname and t["list_names"].strip().find(key) >= 0:
            result.append(t)
    return result
