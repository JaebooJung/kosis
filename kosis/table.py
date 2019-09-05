# -*- coding: utf-8 -*-

import requests
import xmltodict

from .config import get_apikey

__all__ = ["get_metainfo"]


def get_metainfo(org_id, table_id):
    """기관 아이디, 테이블 아이디를 입력하면 기관명, 테이블명, 수록항목, 수록기간 등의 메타정보를 반환

    :param org_id:
    :param table_id:
    :return:
    """
    url = "http://kosis.kr/openapi/statisticsData.do"
    params = {
        "format": "xml",
        "method": "getMeta",
        "apiKey": get_apikey(),
        "orgId": org_id,
        "tblId": table_id
    }

    params.update({"type": "ORG"})
    res = requests.get(url, params=params)
    data = xmltodict.parse(res.content.decode("utf-8"), dict_constructor=dict)
    org_name = data["response"]["Structures"]["orgNm"]

    params.update({"type": "TBL"})
    res = requests.get(url, params=params)
    data = xmltodict.parse(res.content.decode("utf-8"), dict_constructor=dict)
    table_name = data["response"]["Structures"]["tblNm"]

    params.update({"type": "ITM"})
    res = requests.get(url, params=params)
    data = xmltodict.parse(res.content.decode("utf-8"), dict_constructor=dict)
    item = data["response"]["Structures"]["MetaRow"]

    params.update({"type": "PRD"})
    res = requests.get(url, params=params)
    data = xmltodict.parse(res.content.decode("utf-8"), dict_constructor=dict)
    duration = data["response"]["Structures"]

    all_data = {
        "table_name": table_name,
        "org_name": org_name,
        "item": item,
        "duration": duration,
    }
    return all_data
