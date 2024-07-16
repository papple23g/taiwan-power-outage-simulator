import calendar
import datetime
from pprint import pprint

from gnews import GNews
from pydantic import BaseModel, Field, HttpUrl, model_validator


class News(BaseModel):
    date: datetime.date = Field(...)
    title: str
    url: HttpUrl

    @model_validator(mode='before')
    @classmethod
    def set_date(cls, news_dict: dict):
        news_dict['date'] = (
            datetime.datetime.strptime(
                news_dict['published date'],
                '%a, %d %b %Y %H:%M:%S %Z',
            ).date()
        )
        return news_dict


def get_news_list(
    year_int: int,
    month_int: int,
) -> list[News]:

    start_date = datetime.date(year_int, month_int, 1)
    last_day_of_month = calendar.monthrange(
        start_date.year, start_date.month
    )[1]
    end_date = datetime.date(year_int, month_int, last_day_of_month)
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

    raw_news_dict_list = google_news.get_news('"停電" AND "戶"')
    return [
        news
        for news_dict in raw_news_dict_list
        if "停電" in (news := News(**news_dict)).title
    ]


if __name__ == '__main__':

    # # 2017年 815大停電
    # start_date=datetime.date(2017, 8, 15),
    # end_date=datetime.date(2017, 8, 16),

    # # 2021年5月 兩次大停電
    # start_date=datetime.date(2021, 5, 1),
    # end_date=datetime.date(2021, 6, 1),

    # # 最近停電
    # start_date=datetime.date(2024, 5, 12),
    # end_date=datetime.date(2024, 5, 13),

    news_list = get_news_list(
        year_int=2014,
        month_int=2,
    )
    for news in news_list:
        print(news.model_dump_json(indent=2))
        print()
