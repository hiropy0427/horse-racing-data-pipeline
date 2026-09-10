"""取得した払戻データを整理する処理"""

import re
import pandas as pd


def payout_to_number(value):
    """「1,230円」などの文字列から数値だけを取り出す"""

    if value is None or pd.isna(value):
        return pd.NA

    text = str(value).strip()

    if text in {"", "-", "nan", "None", "<NA>"}:
        return pd.NA

    # 数字以外を削除
    digits = re.sub(r"[^\d]", "", text)

    if not digits:
        return pd.NA

    return int(digits)


def parse_payout_text(value):
    """払戻情報の文字列から券種ごとの金額を取得する"""

    result = {
        "quinella": pd.NA,
        "trio": pd.NA,
        "trifecta": pd.NA,
    }

    if value is None or pd.isna(value):
        return pd.Series(result)

    # 表記ゆれに対応
    ticket_name_map = {
        "馬連": "quinella",
        "三連複": "trio",
        "３連複": "trio",
        "三連単": "trifecta",
        "３連単": "trifecta",
    }

    sections = re.split(r"\s*\|\|\s*", str(value).strip())

    for section in sections:
        fields = [item.strip() for item in section.split("|")]

        if len(fields) < 3:
            continue

        ticket_type = fields[0]
        payout = fields[2]

        output_name = ticket_name_map.get(ticket_type)

        if output_name:
            result[output_name] = payout_to_number(payout)

    return pd.Series(result)


def tidy_payouts(raw_df):
    """払戻データを整形し、race_idごとに1行へまとめる"""

    required = {"race_id", "payout_text"}
    missing = required - set(raw_df.columns)

    if missing:
        raise ValueError(f"必要な列がありません: {sorted(missing)}")

    # 文字列の払戻情報を列ごとに分解
    parsed = raw_df["payout_text"].apply(parse_payout_text)

    output = pd.concat(
        [
            raw_df[["race_id"]].reset_index(drop=True),
            parsed
        ],
        axis=1,
    )

    # race_idが重複している場合は最後のデータを残す
    output = output.drop_duplicates(
        subset=["race_id"],
        keep="last"
    )

    # 払戻金額を数値型へ変換
    for column in ["quinella", "trio", "trifecta"]:
        output[column] = pd.to_numeric(
            output[column],
            errors="coerce"
        ).astype("Int64")

    return output.sort_values("race_id").reset_index(drop=True)
