EMOJI_TO_KW_LIST_DICT = {
    "👷": [
        "操作失誤", "看錯班表"
    ],
    "🚧": [
        "施工", "工程", "挖土機", "怪手",
    ],
    "👮": [
        "員警",
    ],
    "🔥": [
        "火災", "起火", "消防救災",
    ],
    "🔧": [
        "檢修", "查修", "遷移作業",
    ],
    "✂️": [
        "剪",
    ],
    "🌳": [
        "樹倒", "樹木", "大樹", "路樹",
    ],
    "💥": [
        "氣爆", "爆炸",
    ],
    "🙋": [
        "民眾", "不明人士",
    ],
    "🚚": [
        "吊車",
    ],
    "🌋": [
        "地震",
    ],
    "🌀": [
        "颱風",
    ],
    "🌪️": [
        "風",
    ],
    "🏮": [
        "廟會",
    ],
    "🤍👃🏻": [
        "白鼻心",
    ],
    "🐦": [
        "鳥", "麻雀", "老鷹", "鸚鵡",
    ],
    "🐿️": [
        "松鼠", "飛鼠",
    ],
    "🐒": [
        "猴子",
    ],
    "🥥": [
        "椰子",
    ],
    "⛈︎": [
        "雷雨", "雷電",
    ],
    "🐾": [
        "動物",
    ],
    "🚗": [
        "車",
    ],
    "🐍": [
        "蛇",
    ],
    "🐈︎": [
        "貓",
    ],
    "🐀": [
        "老鼠",
    ],
    "🐜": [
        "白蟻",
    ],
    "⚡": [
        "負載", "高壓", "電流", "過載", "避雷器",
    ],
    "🧂": [
        "鹽害",
    ],
    "⛰︎⚠️": [
        "落石", "公路崩坍",
    ],
    "🔌": [
        "分支", "分歧", "跳脫", "故障", "地下", "機組", "線路", "匯流", "匯流", "保險絲", "饋線", "電桿", "電線桿", "變電所", "電廠", "電纜", "端頭", "熔絲", "開關",
    ],
    "😷": [
        "懸浮微粒",
    ],
    "❓": [
        "不明",
    ],
}


def get_reason_emoji(reason: str) -> str:
    for reason_emoji, reason_kw_str_list in EMOJI_TO_KW_LIST_DICT.items():
        if any(
            reason_kw_str in reason
            for reason_kw_str in reason_kw_str_list
        ):
            return reason_emoji
    return ""
