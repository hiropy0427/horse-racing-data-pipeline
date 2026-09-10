"""データの欠損や重複を確認するための処理"""

import pandas as pd


def validate_required_columns(df, required):
    """必要な列がそろっているか確認する"""
    return [
        column
        for column in required
        if column not in df.columns
    ]


def find_duplicate_entries(df):
    """同一レース内で重複しているデータを探す"""

    required = ["race_id", "horse_number"]
    missing = validate_required_columns(df, required)

    if missing:
        raise ValueError(f"必要な列がありません: {missing}")

    return df[
        df.duplicated(
            subset=required,
            keep=False
        )
    ].copy()


def find_missing_dates(df, date_column="date", weekend_only=True):
    """データ期間内で登録されていない日付を確認する"""

    if date_column not in df.columns:
        raise ValueError(
            f"日付列がありません: {date_column}"
        )

    dates = (
        pd.to_datetime(
            df[date_column],
            errors="coerce"
        )
        .dropna()
        .dt.normalize()
    )

    if dates.empty:
        return []

    # 最古の日付から最新の日付までを作成
    expected = pd.date_range(
        dates.min(),
        dates.max(),
        freq="D"
    )

    # 週末だけを確認したい場合
    if weekend_only:
        expected = expected[
            expected.dayofweek.isin([5, 6])
        ]

    existing = set(dates)

    # データに存在しない日を候補として返す
    return [
        date
        for date in expected
        if date not in existing
    ]


def validation_summary(df):
    """件数・レース数・重複件数をまとめて確認する"""

    duplicates = find_duplicate_entries(df)

    return {
        "rows": len(df),
        "races": df["race_id"].nunique(),
        "duplicate_rows": len(duplicates),
    }
