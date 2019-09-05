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
    "print_tree",
    "get_tables",
    "search_tables",
    "search_tables_by_id",
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
    """통계 카테고리와 코드 인쇄"""
    len_command = max(*[len(k) for k in category2wv_code.keys()])
    len_text = max(*[len(dict_wv_code.get(v)) for v in category2wv_code.values()])
    format_str = Template(" {:$l1}: {:$l2}").substitute(l1=len_command + 1, l2=len_text)
    for k, v in category2wv_code.items():
        print(format_str.format(k, dict_wv_code.get(v)))


def fetch_nodes(category="topic", parent_list_id=None, parent_name=None, list_map=None):
    """KOSIS에서 트리 전체 정보 다운로드"""
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
                "acc_name": d["LIST_NM"] if parent_name is None else parent_name + ";" + d["LIST_NM"],
                "acc_id": d["LIST_ID"] if parent_list_id is None else parent_list_id + ";" + d["LIST_ID"],
                "id": d["LIST_ID"]
            })
            list_map.update({d["LIST_ID"]: parent_list_id})
        if "TBL_NM" in d:
            list_id = parent_list_id
            list_ids = parent_list_id
            while list_id is not None:
                list_id = list_map[list_id]
                if list_id is not None:
                    list_ids = list_id + ";" + list_ids
            data.append({
                "category": category,
                "type": "table",
                "name": d["TBL_NM"],
                "list_names": parent_name,
                "list_ids": list_ids,
                "id": d["TBL_ID"],
                "org_id": d["ORG_ID"],
            })

    return data


def fetch_subnodes(category="topic", parent_list_id=None, parent_name=None, max_level=1e9, level=0, list_map=None):
    level += 1
    if level > max_level:
        return []
    if parent_list_id is not None:
        print("parent_list_id =", parent_list_id)
    first_nodes = fetch_nodes(category=category, parent_list_id=parent_list_id, parent_name=parent_name,
                              list_map=list_map)
    nodes = []
    for n in first_nodes:
        if n["type"] == "list":
            n["children"] = fetch_subnodes(category=category, parent_list_id=n["id"], parent_name=n["acc_name"],
                                           max_level=max_level, level=level, list_map=list_map)

        nodes.append(n)
    return nodes


def fetch_tree(category=None, max_level=1e9):
    json_path = os.path.join(os.path.dirname(__file__), category + ".json")
    if not os.path.exists(json_path):
        with open(json_path, "w") as json_file:
            json_file.write("{}")
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    nodes = fetch_subnodes(category=category, max_level=max_level, list_map={})
    json_data[category] = nodes
    json_data[category + "-timestamp"] = dt.datetime.now().isoformat()
    with open(json_path, "w") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=2)


def get_tree(category="topic"):
    """트리 객체 반환"""
    json_path = os.path.join(os.path.dirname(__file__), category + ".json")
    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)
    return json_data


def node_copy(node, with_children=False):
    keys = ["category", "type", "name", "id", "org_id", "list_names", "list_ids"]
    if with_children:
        keys.append("children")
    return {k: v for k, v in node.items() if k in keys}


def search_node(result, nodes, key=None, by="name", with_children=False):
    if key is None:
        raise ValueError("key is None")
    for n in nodes:
        if by == "name":
            if (n["type"] == "table") and (n[by].strip().find(key) >= 0):
                n_copy = node_copy(n, with_children)
                result.append(n_copy)
        if by == "id":
            if n[by] == key:
                n_copy = node_copy(n, with_children)
                result.append(n_copy)
        if "children" in n:
            result = search_node(result, n["children"], key, by, with_children)
    return result


def search_tree(key, by="name", category="topic"):
    json_data = get_tree(category)
    nodes = json_data[category]
    result = []
    result = search_node(result, nodes, key, by)
    return result


def search_tablenode(result, nodes):
    for n in nodes:
        if n["type"] == "table":
            n_copy = node_copy(n)
            result.append(n_copy)
        if "children" in n:
            result = search_tablenode(result, n["children"])
    return result


def get_tables(category="topic"):
    """모든 테이블 반환"""
    json_data = get_tree(category)
    nodes = json_data[category]
    result = []
    result = search_tablenode(result, nodes)
    return result


def search_tables(key, search_listname=False, category="topic"):
    """키워드로 테이블 검색"""
    tables = get_tables(category)
    result = []
    for t in tables:
        if t["name"].strip().find(key) >= 0:
            result.append(t)
        if search_listname and t["list_names"].strip().find(key) >= 0:
            result.append(t)
    return result


def search_tables_by_id(table_id, category="topic"):
    """테이블 아이디로 테이블 검색"""
    tables = get_tables(category)
    for t in tables:
        if t["id"] == table_id:
            return t
    return None


def print_nodes(nodes, max_level, parent_last):
    cur_level = len(parent_last)
    if cur_level >= max_level:
        return
    num_nodes = len(nodes)
    parent_last_with_true = parent_last.copy()
    parent_last_with_true.append(True)
    parent_last_with_false = parent_last.copy()
    parent_last_with_false.append(False)
    leadings = "".join(["   " if p else "│ " for p in parent_last])
    if num_nodes == 1:
        node = nodes[0]
        print(leadings + "└─ {name} [{type}:{id}]".format(**node))
        parent_last.append(False)
        if "children" in node:
            print_nodes(node["children"], max_level, parent_last_with_false)
    else:
        for i, node in enumerate(nodes):
            if i == num_nodes - 1:
                print(leadings + "└─ {name} [{type}:{id}]".format(**node))
                if "children" in node:
                    print_nodes(node["children"], max_level, parent_last_with_true)
            else:
                print(leadings + "├─ {name} [{type}:{id}]".format(**node))
                if "children" in node:
                    print_nodes(node["children"], max_level, parent_last_with_false)


def print_tree(list_id=None, max_level=1, category="topic"):
    """트리 프린트"""
    tree = get_tree(category)[category]
    if list_id is None:
        nodes = tree
    else:
        result = []
        result = search_node(result, tree, list_id, by="id", with_children=True)
        nodes = result[0]["children"]
    print_nodes(nodes, max_level, [])
