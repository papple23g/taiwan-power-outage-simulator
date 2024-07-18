from libs.news import NEWS_LIST_JSON_PATH, NewsList

if __name__ == '__main__':
    # 讀取現有的新聞列表資料
    news_list = NewsList.model_validate_json(
        NEWS_LIST_JSON_PATH.read_text(encoding="utf-8")
    ).root

    # # 排序新聞列表資料
    # news_list.sort(key=lambda news: news.date)
    # # 將新聞列表資料寫入 JSON 檔
    # NEWS_LIST_JSON_PATH.write_text(
    #     NewsList(news_list).model_dump_json(indent=4),
    #     encoding="utf-8",
    # )

    # # 印出新聞筆數
    # print(f"{len(news_list)=}")

    # # 印出停電筆數
    # print(sum(news.reason is not None for news in news_list))

    # # 印出停電原因
    # reason_set = {
    #     news.reason
    #     for news in news_list
    #     if news.reason is not None
    # }
    # reason_list = sorted(list(reason_set))
    # for reason in reason_list:
    #     print(reason)

    # # 印出停電地點
    # location_str_set = {
    #     location_str
    #     for news in news_list
    #     if news.locations is not None
    #     for location_str in news.locations
    # }
    # location_str_list = sorted(list(location_str_set))
    # for location_str in location_str_list:
    #     print(location_str)

    blackout_news_list = [
        news
        for news in news_list
        if news.reason is not None
    ]
    print([
        {
            "date": news.date,
            "households": news.households,
        }
        for news in blackout_news_list[-10:]
    ])
