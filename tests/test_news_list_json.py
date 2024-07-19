import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))  # noqa
from libs.news import NEWS_LIST_JSON_PATH, NewsList
from libs.reason_emoji import get_reason_emoji


def test_news_list_json_locations():
    """ 測試新聞列表資料中的縣市名稱是否正確
    """

    # 讀取現有的新聞列表資料中的縣市名稱
    news_list = NewsList.model_validate_json(
        NEWS_LIST_JSON_PATH.read_text(encoding="utf-8")
    ).root
    news_list_city_name_set: set[str] = {
        city_name
        for news in news_list
        if news.locations is not None
        for city_name in news.locations
    }

    # 讀取台灣縣市名稱
    geojson_path = (
        Path(__file__).parent.parent /
        "data/twCounty2010merge.geojson"
    )
    geojson_dict = json.load(geojson_path.open('r', encoding='utf-8'))
    city_name_set = {
        city_dict["properties"]["COUNTYNAME"]
        for city_dict in geojson_dict["features"]
    }
    invalid_city_name_set = news_list_city_name_set - city_name_set

    assert len(invalid_city_name_set) == 0, \
        f"縣市名稱不正確 ({invalid_city_name_set})，必須為以下之一: {news_list_city_name_set}"


def test_news_list_json_reason_emoji():
    """ 測試新聞列表資料中的停電原因是否有對應的 emoji
    """

    # 讀取現有的新聞列表資料中的縣市名稱
    news_list = NewsList.model_validate_json(
        NEWS_LIST_JSON_PATH.read_text(encoding="utf-8")
    ).root

    for news in news_list:
        if news.reason is None:
            continue
        reason_emoji = get_reason_emoji(news.reason)
        assert reason_emoji != "", f"此停電原因沒有對應的 emoji: {news.reason} ({news.date=}, {news.title=})"
