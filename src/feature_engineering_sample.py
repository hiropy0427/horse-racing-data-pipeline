"""公開可能な範囲の特徴量生成サンプル"""

import pandas as pd


def add_basic_features(df):
    """基本的な特徴量を追加する"""

    required = {"race_id", "horse_id", "horse_number", "date"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"必要な列がありません: {sorted(missing)}")

    df = df.copy()

    # 日付と馬番を扱いやすい型に変換
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["horse_number"] = pd.to_numeric(
        df["horse_number"],
        errors="coerce"
    )

    # レースごとの出走頭数を計算
    df["field_size"] = (
        df.groupby("race_id")["race_id"]
        .transform("size")
    )

    # 馬番が出走頭数の中でどの位置にあるかを割合にする
    df["horse_number_ratio"] = (
        df["horse_number"] / df["field_size"]
    )

    # 馬ごとに日付順へ並べ、前走からの日数を計算
    df = df.sort_values(["horse_id", "date"])

    df["days_since_previous"] = (
        df.groupby("horse_id")["date"]
        .diff()
        .dt.days
    )

    return df.sort_index()


# 実際の開発では、このほかにも多数の特徴量を作成しています。
# 予測精度に関わる独自の計算式・条件・組み合わせは公開していません。
