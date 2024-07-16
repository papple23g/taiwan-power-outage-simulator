from main import NEWS_LIST_JSON_PATH, NewsList

if __name__ == '__main__':

    # 讀取現有的新聞列表資料
    news_list = NewsList.model_validate_json(
        NEWS_LIST_JSON_PATH.read_text(encoding="utf-8")
    ).root
    news_list.sort(key=lambda news: news.date)
    # 將新聞列表資料寫入 JSON 檔
    NEWS_LIST_JSON_PATH.write_text(
        NewsList(news_list).model_dump_json(indent=4),
        encoding="utf-8",
    )
