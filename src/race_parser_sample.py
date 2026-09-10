"""保存済みHTMLを解析してDataFrameにするサンプル"""

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup


def normalize_text(value):
    """余分な空白や改行を整える"""
    return re.sub(r"\s+", " ", value or "").strip()


def parse_result_table(html, record_id):
    """HTML内の表から基本情報を取得する"""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.result")

    if table is None:
        return []

    rows = []

    for tr in table.select("tbody tr"):
        cells = tr.find_all("td", recursive=False)

        # 必要な列が足りない行は除外
        if len(cells) < 5:
            continue

        rows.append(
            {
                "record_id": record_id,
                "horse_number": normalize_text(cells[0].get_text(" ", strip=True)),
                "horse_name": normalize_text(cells[1].get_text(" ", strip=True)),
                "jockey": normalize_text(cells[2].get_text(" ", strip=True)),
                "finish": normalize_text(cells[3].get_text(" ", strip=True)),
                "odds": normalize_text(cells[4].get_text(" ", strip=True)),
            }
        )

    return rows


def parse_directory(html_dir):
    """フォルダ内のHTMLをまとめて読み込み、DataFrameに変換する"""
    records = []

    for path in sorted(html_dir.glob("record_*.html")):
        record_id = path.stem.replace("record_", "")
        html = path.read_text(encoding="utf-8")

        records.extend(
            parse_result_table(html, record_id)
        )

    df = pd.DataFrame(records)

    if df.empty:
        return df

    # 数値として扱いたい列を変換
    df["horse_number"] = pd.to_numeric(df["horse_number"], errors="coerce")
    df["finish"] = pd.to_numeric(df["finish"], errors="coerce")
    df["odds"] = pd.to_numeric(df["odds"], errors="coerce")

    # 同一レース・同一馬番の重複を削除
    df = df.drop_duplicates(
        subset=["record_id", "horse_number"]
    )

    return df.reset_index(drop=True)


if __name__ == "__main__":
    dataframe = parse_directory(Path("data/html"))
    print(dataframe.head())
