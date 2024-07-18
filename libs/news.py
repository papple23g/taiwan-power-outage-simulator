import calendar
import datetime
from pathlib import Path

from gnews import GNews
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl, RootModel, model_validator

# 初始化新聞列表資料 JSON 檔
NEWS_LIST_JSON_PATH = (
    Path(__file__).parent.parent / 'data/news_list.json'
)
NEWS_LIST_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
if not NEWS_LIST_JSON_PATH.exists():
    NEWS_LIST_JSON_PATH.write_text('[]')
# exit()


class News(BaseModel):
    date: datetime.date = Field(...)
    title: str
    url: HttpUrl
    households: int | None = None
    """停電戶數"""
    locations: list[str] | None = None
    """停電縣市"""
    reason: str | None = None
    """停電原因"""

    @model_validator(mode='before')
    @classmethod
    def set_date(cls, news_dict: dict):
        if 'published date' in news_dict:
            news_dict['date'] = (
                datetime.datetime.strptime(
                    news_dict['published date'],
                    '%a, %d %b %Y %H:%M:%S %Z',
                ).date()
            )
        return news_dict

    def __str__(self) -> str:
        return f"{self.date:%Y-%m-%d}: {self.title}"


class NewsList(RootModel[list[News]]):
    pass


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


def update_news_list_json(
    start_year_month_int_tuple: tuple[int, int],
    end_year_month_int_tuple: tuple[int, int],
):
    start_year_int, start_month_int = start_year_month_int_tuple
    end_year_int, end_month_int = end_year_month_int_tuple

    month_1st_date = datetime.date(start_year_int, start_month_int, 1)

    # 讀取現有的新聞列表資料
    news_list = NewsList.model_validate_json(
        NEWS_LIST_JSON_PATH.read_text(encoding="utf-8")
    ).root
    # print(news_list)

    try:
        while (month_1st_date.year, month_1st_date.month) <= (end_year_int, end_month_int):

            logger.info(
                f"正在獲取 {month_1st_date.year}年{month_1st_date.month:02d}月 的停電新聞"
            )
            _news_list = get_news_list(
                year_int=month_1st_date.year,
                month_int=month_1st_date.month,
            )
            _news_list.sort(key=lambda news: news.date)
            for _news in _news_list:
                logger.debug(_news)
            logger.success(f"共獲取 {len(_news_list)} 筆新聞")
            news_list.extend(_news_list)

            # 跳至下一個月
            month_1st_date = datetime.date(
                month_1st_date.year + (month_1st_date.month // 12),
                (month_1st_date.month % 12) + 1,
                1,
            )
    except Exception as e:
        logger.error(e)
    finally:
        # 將新聞列表資料寫入 JSON 檔
        NEWS_LIST_JSON_PATH.write_text(
            NewsList(news_list).model_dump_json(indent=4),
            encoding="utf-8",
        )
        logger.success(f"新聞列表資料已寫入 {NEWS_LIST_JSON_PATH}")


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

    # news_list = get_news_list(
    #     year_int=2014,
    #     month_int=2,
    # )
    # for news in news_list:
    #     print(news.model_dump_json(indent=2))
    #     print()

    update_news_list_json(
        start_year_month_int_tuple=(2014, 1),
        end_year_month_int_tuple=(2024, 7),
    )
