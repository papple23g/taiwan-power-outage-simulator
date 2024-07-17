import json
from pathlib import Path

geojson_path = Path(__file__).parent/"twCounty2010merge.geojson"
geojson_dict = json.load(geojson_path.open('r', encoding='utf-8'))
city_name_list = [
    city_dict["properties"]["COUNTYNAME"]
    for city_dict in geojson_dict["features"]
]
for city_name in city_name_list:
    print(city_name)
