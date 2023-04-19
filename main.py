import requests
from bs4 import BeautifulSoup
import os
import time
import traceback
import sys


def get_last_page(tag: str) -> int:
    url = f"https://danbooru.donmai.us/posts?tags={tag}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return int(soup.select_one(".paginator > :nth-last-child(2)").text)


def get_image_url(link):
    image_page_url = link["href"]
    image_page_html = requests.get(f"https://danbooru.donmai.us{image_page_url}").text
    image_soup = BeautifulSoup(image_page_html, "html.parser")
    return image_soup.select_one("#image")["src"]


def download_image(image_url: str, file_name: str):
    response = requests.get(image_url, stream=True)
    with open(file_name, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def download_images(tag: str):
    last_page = get_last_page(tag)
    os.makedirs("images", exist_ok=True)

    count = 0
    for i in range(1, last_page + 1):
        try:
            url = f"https://danbooru.donmai.us/posts?tags={tag}&page={i}"
            print(f"[INFO] {i}ページ目を開いています...")
            html = requests.get(url).text
            soup = BeautifulSoup(html, "html.parser")
            for link in soup.select("article > div > a"):
                try:
                    image_url = get_image_url(link)
                    file_name = os.path.join("images", os.path.basename(image_url))
                    download_image(image_url, file_name)
                    count += 1
                    print(f"[INFO] {count}個目の画像({file_name})をダウンロードしました。")
                    time.sleep(1)
                except:
                    print(f"[ERROR] 画像のダウンロードに失敗しました。URL: {link['href']}")
                    print(traceback.format_exc())
        except:
            print(f"[ERROR] ページの取得に失敗しました。URL: {url}")
            print(traceback.format_exc())

    print(f"[INFO] 全{count}個の画像をダウンロードしました。")


if __name__ == "__main__":
    tag = sys.argv[1]
    download_images(tag)
