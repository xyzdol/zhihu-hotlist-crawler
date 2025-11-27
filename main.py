import requests
import json
from datetime import datetime
import csv
import argparse
import os

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
    return hot_list

def save_to_json(hot_list, timestamp, output_dir):
    filename = f"zhihu_hot_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(hot_list, f, ensure_ascii=False, indent=2)

    print(f"Hot list saved to {filepath}")

def save_to_csv(hot_list, timestamp, output_dir):
    filename = f"zhihu_hot_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Hot", "Link"])
        for item in hot_list:
            writer.writerow([item["title"], item["hot"], item["link"]])
    print(f"CSV file saved to {filepath}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-json", action="store_true")
    parser.add_argument("--no-csv", action="store_true")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--output-dir", type=str, default=".")
    return parser.parse_args()


def main():
    args = parse_args()
    data = fetch_zhihu_hotlist()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)


    if args.limit:
        data = data[:args.limit]
    if args.preview:
        for i in range(min(len(data), 3)):
            print(data[i]["title"], data[i]["hot"], data[i]["link"])

    if not args.no_json:
        save_to_json(data, timestamp, output_dir)
    if not args.no_csv:
        save_to_csv(data, timestamp, output_dir)

    print("Successfully Done!")

if __name__ == "__main__":
    main()

