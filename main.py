import time
import schedule
import requests
from requests.exceptions import RequestException
import json
from datetime import datetime
import csv
import argparse
import os
import logging

url = "https://api.zhihu.com/topstory/hot-list"
headers = {
    "User-Agent": "Mozilla/5.0"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def fetch_with_retry(max_attempt):
    for i in range(max_attempt):
        logging.info(f"Fetching Zhihu hot list, attempt {i + 1}")
        try:
            resp = requests.get(url, headers=headers, timeout=5)
        except RequestException as e:
            logging.warning(f"Request failed {url}: {e}")
            logging.warning(f"Retrying... Attempt{i + 1}/{max_attempt}")
            time.sleep(2 ** i)
            continue
        return resp
    logging.error(f"Max retry reached, Failed in fetching {url}")
    return None

def parse_zhihu_json(resp):
    logging.info(f"Status code: {resp.status_code}")
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
        logging.info(f"Saving json to {filepath}")
        json.dump(hot_list, f, ensure_ascii=False, indent=2)

    # print(f"Hot list saved to {filepath}")
    logging.info(f"Saved json to {filepath}")

def save_to_csv(hot_list, timestamp, output_dir):
    filename = f"zhihu_hot_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        logging.info(f"Saving csv to {filepath}")
        writer = csv.writer(f)
        writer.writerow(["Title", "Hot", "Link"])
        for item in hot_list:
            writer.writerow([item["title"], item["hot"], item["link"]])
    logging.info(f"Saved csv to {filepath}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-json", action="store_true")
    parser.add_argument("--no-csv", action="store_true")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--output-dir", type=str, default=".")
    parser.add_argument("--max-attempt", type=int, default=3)
    parser.add_argument("--interval", type=int, default=1)
    return parser.parse_args()

def run_once(args):
    resp = fetch_with_retry(args.max_attempt)
    if not resp:
        logging.error("Failed to fetch Zhihu hot list")
        return
    data = parse_zhihu_json(resp)
    if not data:
        logging.error("Failed to parse Zhihu hot list")
        return
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

    # print("Successfully Done!")
    logging.info("Job finished, waiting for next schedule")

def main():
    args = parse_args()
    # data = fetch_zhihu_hotlist()
    interval = args.interval
    run_once(args)
    schedule.every(interval).minutes.do(run_once, args)
    logging.info("Starting scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(1)




# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    main()