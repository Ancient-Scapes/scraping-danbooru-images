import requests
from bs4 import BeautifulSoup
import os
import time
import traceback
import sys

# ダウンロードするタグを指定する
tag = sys.argv[1]

# 最後のページ番号を取得する
url = f"https://danbooru.donmai.us/posts?tags={tag}"
html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")
last_page = int(soup.select_one(".paginator > :nth-last-child(2)").text)

# 画像を保存するフォルダを作成する
os.makedirs("images", exist_ok=True)

# 各画像ページから画像URLを取得して、画像をダウンロードする
count = 0  # ダウンロードした画像の数をカウントする
for i in range(1, last_page + 1):
    try:
        url = f"https://danbooru.donmai.us/posts?tags={tag}&page={i}"
        print(f"[INFO] {i}ページ目を開いています...")
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.select("article > div > a"):
            image_page_url = link["href"]
            image_page_html = requests.get(f"https://danbooru.donmai.us{image_page_url}").text
            image_soup = BeautifulSoup(image_page_html, "html.parser")
            image_url = image_soup.select_one("#image")["src"]
            file_name = os.path.join("images", os.path.basename(image_url))
            response = requests.get(image_url, stream=True)
            with open(file_name, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            count += 1
            print(f"[INFO] {count}個目の画像({file_name})をダウンロードしました。")
            time.sleep(1)  # 過剰な負荷をかけないようにするために1秒待つ
    except Exception as e:
        print(f"[ERROR] 画像のダウンロードに失敗しました。URL: {url}")
        print(traceback.format_exc())  # エラー内容を出力する

print(f"[INFO] 全{count}個の画像をダウンロードしました。")
