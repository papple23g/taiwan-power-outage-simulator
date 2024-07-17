import datetime
from pprint import pprint

from gnews import GNews

start_date = datetime.date(2024, 5, 18)
end_date = (
    start_date+datetime.timedelta(days=1)
)

google_news = GNews(
    language='zh-Hant',
    country='TW',
    start_date=start_date,
    end_date=end_date,
    max_results=100,
    # proxy=proxy,
    exclude_websites=[
        'https://www.cw.com.tw',  # 天下雜誌
        'https://www.parenting.com.tw',  # 親子天下
        'https://www.ithome.com.tw',  # iThome
        'https://news.housefun.com.tw',  # 好房網
        'https://www.soft4fun.net',  # 硬是要學
    ]
)

raw_news_dict_list = google_news.get_news("停電")
pprint(raw_news_dict_list)
