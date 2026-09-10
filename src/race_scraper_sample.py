"""Seleniumを使ったWebデータ取得のサンプル"""

import random
import time
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# アクセス間隔やリトライ回数
MIN_DELAY = 2.0
MAX_DELAY = 5.0
MAX_RETRIES = 3
PAGE_TIMEOUT = 30


def build_driver():
    """ChromeDriverを起動する"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.set_page_load_timeout(PAGE_TIMEOUT)
    return driver


def random_wait():
    """連続アクセスを避けるため、少し待機する"""
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def fetch_html(driver, url, required_selector):
    """ページを取得し、HTMLを返す"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            driver.get(url)

            # 必要な要素が表示されるまで待機
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, required_selector)
                )
            )
            return driver.page_source

        except WebDriverException as e:
            print(f"取得失敗 {attempt}/{MAX_RETRIES}: {e}")
            random_wait()

    return None


def save_if_missing(output_dir, record_id, html):
    """すでに保存済みの場合は上書きせず、新しいデータだけ保存する"""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"record_{record_id}.html"

    if output_path.exists():
        print(f"取得済みのためスキップ: {output_path.name}")
        return False

    output_path.write_text(html, encoding="utf-8")
    print(f"保存完了: {output_path.name}")
    return True


def collect_records(record_ids, url_template, required_selector, output_dir):
    """複数のIDを順番に取得する"""
    driver = build_driver()

    try:
        for record_id in record_ids:
            output_path = output_dir / f"record_{record_id}.html"

            # 取得済みデータは再取得しない
            if output_path.exists():
                print(f"取得済み: {record_id}")
                continue

            url = url_template.format(record_id=record_id)
            html = fetch_html(driver, url, required_selector)

            if html is not None:
                save_if_missing(output_dir, record_id, html)

            random_wait()

    finally:
        driver.quit()


if __name__ == "__main__":
    # 公開用のため、実際に使用しているURL・ID・セレクタは掲載していません
    sample_ids = ["SAMPLE001", "SAMPLE002"]

    collect_records(
        record_ids=sample_ids,
        url_template="https://example.invalid/records/{record_id}",
        required_selector="table.result",
        output_dir=Path("data/html"),
    )
