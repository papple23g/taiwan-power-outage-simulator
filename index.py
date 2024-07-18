import datetime
import json
from collections import defaultdict
from dataclasses import dataclass
from itertools import groupby

from browser import doc, timer, window
from browser.html import AUDIO, INPUT, SOURCE, SVG

from libs.type_hint import D3

d3: D3 = window.d3
tw_svg: D3 = None


@dataclass
class News:
    """ 停電新聞
    """
    date: datetime.date
    title: str
    households: int | None = None
    """停電戶數"""
    locations: list[str] | None = None
    """停電縣市"""
    reason: str | None = None
    """停電原因"""

    @classmethod
    def from_dict(cls, news_dict: dict) -> 'News':
        return cls(
            date=(
                datetime.datetime.strptime(
                    news_dict['date'],
                    "%Y-%m-%d",
                ).date()
            ),
            title=news_dict['title'],
            households=news_dict['households'],
            locations=news_dict['locations'],
            reason=news_dict['reason'],
        )


# 載入新聞串列
news_dict_list: list[dict] = json.load(
    open("data/news_list.json", "r", encoding="utf-8")
)
# window.console.log(news_dict_list)
# print(f"{len(news_dict_list)=}")
news_list = [
    News.from_dict(news_dict)
    for news_dict in news_dict_list
    if news_dict.get("households", 0) > 0
]
# print(f"{len(news_list)=}")

# 🐛debug: 測試一小段近十筆資料
news_list = news_list[-100:]

# 以日期分組新聞串列
date_to_news_list_dict = {
    date: list(news_iter)
    for date, news_iter in groupby(
        news_list,
        key=lambda news: news.date,
    )
}
# print(date_to_news_list_dict)
# exit()

# 各縣市的停電比值字典
CITY_TO_BLACKOUT_RATIO_DICT = defaultdict(int)


def get_blackout_rgb_str(blackout_ratio: float) -> str:
    """ 根據停電比值返回對應的 RGB 顏色
    Args:
        blackout_ratio (float): 停電比值
            0: 黃色
            1: 黑色
    """
    return f"rgb({255 - int(255 * blackout_ratio)}, {255 - int(255 * blackout_ratio)}, 0)"


def update_city_to_blackout_ratio_dict() -> None:
    """ 更新每個縣市的停電比值: 逐漸淡出至 0 (黑色→黃色)
    """
    global CITY_TO_BLACKOUT_RATIO_DICT
    fade_out_duration_sec_int = 5  # 淡出時間 (秒)
    update_per_ms_int = 10
    for city_name, blackout_ratio in CITY_TO_BLACKOUT_RATIO_DICT.items():
        if blackout_ratio > 0:
            CITY_TO_BLACKOUT_RATIO_DICT[city_name] -= (
                update_per_ms_int
                / (fade_out_duration_sec_int * 1000)
            )
        else:
            CITY_TO_BLACKOUT_RATIO_DICT[city_name] = 0


def update_tw_svg(
    city_to_blackout_ratio_dict: dict,
    tw_svg: D3,
) -> None:
    """ 根據停電比值更新 SVG 圖形的填充顏色
    """
    tw_svg.selectAll("path").style(
        "fill", lambda d, i, nodes: (
            get_blackout_rgb_str(
                city_to_blackout_ratio_dict[d["properties"]["name"]]
            )
        )
    )


def simulate_blackout_events(date: datetime.date) -> None:
    """ 模擬指定日期的停電事件: 更新各縣市的停電比值字典
    """
    doc["date_h2"].text = f"{date:%Y-%m-%d}"

    # 設定動畫特效為全黑的戶數
    max_households_threshold = 1_000_000

    # 更新停電比值字典: 設定指定縣市的停電比值
    shut_off_ratio_list = list[float]()
    for news in date_to_news_list_dict.get(date, []):
        for city_name in news.locations:
            shut_off_ratio = (news.households/max_households_threshold)**0.5
            CITY_TO_BLACKOUT_RATIO_DICT[city_name] = min(
                CITY_TO_BLACKOUT_RATIO_DICT[city_name]+shut_off_ratio,
                1.0,
            )
            shut_off_ratio_list.append(shut_off_ratio)

    # 播放停電音效
    if (max_shut_off_ratio := min(sum(shut_off_ratio_list), 1)) > 0:
        power_outage_audio = AUDIO(
            SOURCE(src="audio/power_outage.mp3", type="audio/mpeg")
        )
        power_outage_audio.volume = max_shut_off_ratio
        power_outage_audio.play()


def setup_tw_svg() -> None:
    """ 初始化台灣行政區 SVG
    """
    global tw_svg
    doc["tw_svg_div"] <= SVG(id="tw_svg")

    width = 800
    height = 800

    tw_svg = (
        d3.select("#tw_svg")
        .attr("viewBox", f"0 0 {width} {height}")
    )

    projection = (
        d3.geoMercator()
        .center([121, 24])
        .scale(8000)
        .translate([width / 2, height / 2])
    )

    path = d3.geoPath().projection(projection)

    # 加載 GeoJSON 並繪製地圖
    d3.json("data/twCounty2010merge.geojson").then(lambda data: (
        tw_svg.selectAll("path")
        .data(data["features"])
        .enter().append("path")
        .attr("d", path)
        .attr("stroke", "#000")
        .attr("stroke-width", 1)
    )).catch(lambda error: print(f"加載 GeoJSON 時發生錯誤：{error}"))

    return tw_svg

playing_slider_timer = None

def play_or_pause_slider(slider: INPUT) -> None:
    """ 播放/暫停按鈕的點擊事件處理函數
    """
    global playing_slider_timer

    # 設置播放速度: 每秒播放的天數
    per_sec_day_count = 10

    def add_slider_step() -> None:
        """ 進步滑條的值
        """
        global playing_slider_timer
        # 若已達最大值，則停止播放
        if int(slider.value) == int(slider.max):
            timer.clear_interval(playing_slider_timer)
            playing_slider_timer = None
            return

        slider.value = int(slider.value) + 1
        simulate_blackout_events(
            start_date + datetime.timedelta(days=int(slider.value)),
        )

    # 進行滑條播放或者暫停
    if playing_slider_timer is None:
        playing_slider_timer = timer.set_interval(
            add_slider_step,
            1000/per_sec_day_count,
        )
    else:
        timer.clear_interval(playing_slider_timer)
        playing_slider_timer = None

def on_click_slider(slider: INPUT) -> None:
    """ 滑條的點擊事件處理函數
    """
    global playing_slider_timer

    # 無條件暫停滑條的播放
    if playing_slider_timer is not None:
        timer.clear_interval(playing_slider_timer)
        playing_slider_timer = None

    # 根據滑條的值呈現對應日期的停電事件
    simulate_blackout_events(
        start_date + datetime.timedelta(days=int(slider.value)),
    )

# def main():
if __name__ == '__main__':
    # 初始化 SVG 圖形
    tw_svg = setup_tw_svg()

    # 設定計時器: 不斷更新各縣市停電比值與 SVG 圖形
    update_per_ms_int = 10
    timer.set_interval(
        update_city_to_blackout_ratio_dict,
        update_per_ms_int,
    )
    timer.set_interval(
        lambda: update_tw_svg(
            CITY_TO_BLACKOUT_RATIO_DICT,
            tw_svg,
        ),
        update_per_ms_int,
    )


    # 追加一個播放/暫停按鈕
    doc["slider_div"] <= INPUT(
        type="button",
        value="⏯",
    ).bind(
        "click",
        lambda ev: play_or_pause_slider(slider),
    )


    # 追加日期滑條
    start_date = news_list[0].date - datetime.timedelta(days=1)
    end_date = news_list[-1].date + datetime.timedelta(days=1)
    duration_day_count = (end_date - start_date).days
    doc["date_h2"].text = f"{start_date:%Y-%m-%d}"
    slider = INPUT(
        type="range",
        min=0,
        max=duration_day_count,
        value=0,
        style="width: 100%",
    ).bind(
        "input",
        lambda ev: on_click_slider(slider),
    )
    doc["slider_div"] <= slider

    # 創建圖表配置
    config = {
        'type': 'bar',
        'data': {
            # 'labels': ['2024-07-05', '2024-07-06', '2024-07-07', '2024-07-08', '2024-07-09', '2024-07-16'],
            'labels': [
                news.date.strftime("%Y-%m-%d")
                for news in news_list
            ],
            'datasets': [{
                'label': 'Households',
                # 'data': [5041, 3747, 5291, 14, 60248, 2350],
                'data': [
                    news.households for news in news_list
                ],
                'backgroundColor': 'rgba(75, 192, 192, 0.6)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            }]
        },
        'options': {
            'responsive': True,
            'scales': {
                'y': {
                    'beginAtZero': True,
                    'title': {
                        'display': True,
                        'text': '停電戶數'
                    }
                },
                # 'x': {
                #     'title': {
                #         'display': True,
                #         'text': 'Date'
                #     }
                # }
            },
            'plugins': {
                'title': {
                    'display': True,
                    'text': 'Household Data Histogram'
                }
            }
        }
    }

    # 創建圖表
    Chart = window.Chart.new(doc['chart_div'], config)
