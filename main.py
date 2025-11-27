import requests
import json
from datetime import datetime


def fetch_zhihu_hotlist():
    url = "https://api.zhihu.com/topstory/hot-list"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(url, headers=headers)
    print("Status code:", resp.status_code)

    data = resp.json()

    hot_list = []
    for item in data["data"]:
        title = item["target"]["title"]
        hot = item["detail_text"]
        link = item["target"].get("url")
        hot_list.append({
            "title": title,
            "hot": hot,
            "link": link
        })

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"zhihu_hot_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(hot_list, f, ensure_ascii=False, indent=2)

    print(f"Hot list saved to {filename}")


if __name__ == "__main__":
    fetch_zhihu_hotlist()
