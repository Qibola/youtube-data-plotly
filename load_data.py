"""Load and clean data/trending.csv (Day 2).

The raw CSV is messy on purpose (see README). This module turns it into a tidy
DataFrame that the Plotly charts on later days can trust:

  * `views` arrives as text on some rows ("79,432") -> strip commas, make it int
  * one `likes` value is blank                      -> filled with 0, row kept
  * one row is an exact duplicate                   -> dropped
  * `category` is sometimes SHOUTED ("MUSIC")       -> title-cased
  * one `title` has padding whitespace              -> stripped
  * `publish_date` is text                          -> real datetime64

Run it directly to see a before/after summary:

    python3 load_data.py
"""

from pathlib import Path

import pandas as pd

CSV_PATH = Path(__file__).parent / "data" / "trending.csv"
TEXT_COLS = ["video_id", "title", "channel", "category"]
COUNT_COLS = ["views", "likes", "comments", "duration_sec"]


def load_raw(path: Path = CSV_PATH) -> pd.DataFrame:
    """Read the CSV exactly as it is on disk, with no cleaning."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found - generate it first with: python3 make_sample_data.py"
        )
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a tidied copy of the raw trending DataFrame."""
    df = df.copy()

    # Text columns: drop any padding whitespace.
    for col in TEXT_COLS:
        df[col] = df[col].astype(str).str.strip()

    # "MUSIC" and "Music" are the same category.
    df["category"] = df["category"].str.title()

    # Count columns can arrive as text because of thousands separators or
    # blanks. Strip the commas, coerce to numbers, then fill the gaps.
    for col in COUNT_COLS:
        as_text = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
        df[col] = pd.to_numeric(as_text, errors="coerce").fillna(0).astype("int64")

    df["publish_date"] = pd.to_datetime(df["publish_date"], errors="coerce")

    # The same video listed twice is still one video.
    df = df.drop_duplicates(subset="video_id", keep="first")

    return df.sort_values("views", ascending=False).reset_index(drop=True)


def load_clean(path: Path = CSV_PATH) -> pd.DataFrame:
    """Convenience wrapper: read the CSV and clean it in one call."""
    return clean(load_raw(path))


def main() -> None:
    raw = load_raw()
    tidy = load_clean()

    print(f"raw:   {len(raw)} rows, views dtype = {raw['views'].dtype}")
    print(f"clean: {len(tidy)} rows, views dtype = {tidy['views'].dtype}")
    print(f"dropped {len(raw) - len(tidy)} duplicate row(s)")
    print(f"publish_date dtype = {tidy['publish_date'].dtype}")
    print(f"categories: {sorted(tidy['category'].unique())}")
    print("\ntop 5 by views:")
    print(tidy[["title", "channel", "category", "views", "likes"]].head().to_string(index=False))


if __name__ == "__main__":
    main()
