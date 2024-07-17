import datetime
from collections import defaultdict

from browser import doc, timer, window
from browser.html import AUDIO, INPUT, SOURCE, SVG

from libs.type_hint import D3

d3: D3 = window.d3
tw_svg: D3 = None

# 各縣市的停電比值字典
CITY_TO_BLACKOUT_RATIO_DICT = defaultdict(int)

blackout_event_dict_list = [
    {
        "date": datetime.date(2000, 1, 2),
        "city": "台北市",
        "ratio": 0.2,
    },
    {
        "date": datetime.date(2000, 1, 3),
        "city": "高雄市",
        "ratio": 0.2,
    },
    {
        "date": datetime.date(2000, 1, 5),
        "city": "台南市",
        "ratio": 1.0,
    },
]


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


def shut_off_city(city_name: str, shut_off_ratio: float = 1) -> None:
    """ 關閉指定縣市的電力
    """
    # 更新停電比值字典: 設定指定縣市的停電比值
    global CITY_TO_BLACKOUT_RATIO_DICT
    CITY_TO_BLACKOUT_RATIO_DICT[city_name] = max(
        CITY_TO_BLACKOUT_RATIO_DICT[city_name]+shut_off_ratio,
        1.0,
    )

    # 播放停電音效
    power_outage_audio = AUDIO(
        SOURCE(src="audio/power_outage.mp3", type="audio/mpeg")
    )
    power_outage_audio.volume = shut_off_ratio
    power_outage_audio.play()


def simulate_blackout_events(date: datetime.date) -> None:
    """ 模擬指定日期的停電事件: 更新各縣市的停電比值字典
    """
    for event in blackout_event_dict_list:
        if event["date"] == date:
            shut_off_city(event["city"], event["ratio"])


def setup_tw_svg() -> None:
    """ 初始化台灣行政區 SVG
    """
    global tw_svg
    doc <= SVG(id="tw_svg")

    width = 960
    height = 600

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
    playing_slider_timer = None

    def play_or_pause_slider(slider: INPUT) -> None:
        """ 播放/暫停按鈕的點擊事件處理函數
        """
        global playing_slider_timer

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
                500,
            )
        else:
            timer.clear_interval(playing_slider_timer)
            playing_slider_timer = None

    # 追加一個播放/暫停按鈕
    doc <= INPUT(
        type="button",
        value="⏯",
    ).bind(
        "click",
        lambda ev: play_or_pause_slider(slider),
    )

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

    # 追加一個日期滑條
    start_date = datetime.date(2000, 1, 1)
    end_date = datetime.date(2000, 1, 5)
    duration_day_count = (end_date - start_date).days
    slider = INPUT(
        type="range",
        min=0,
        max=duration_day_count,
        value=0,
    ).bind(
        "input",
        lambda ev: on_click_slider(slider),
    )
    doc <= slider
