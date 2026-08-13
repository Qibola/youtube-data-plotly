"""Day 3 - bar chart of the most-viewed trending videos.

Reads the tidy DataFrame from `load_data.load_clean()`, takes the top N videos
by view count, and writes a standalone interactive HTML file you can open in a
browser (hover for the exact numbers, no server needed).

    python3 chart_top_videos.py            # top 10 -> output/top_videos.html
    python3 chart_top_videos.py --top 5    # just the top 5
"""

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px

from load_data import load_clean

OUTPUT_PATH = Path(__file__).parent / "output" / "top_videos.html"
DEFAULT_TOP = 10


def top_by_views(df: pd.DataFrame, top: int = DEFAULT_TOP) -> pd.DataFrame:
    """Return the `top` highest-viewed rows, most-viewed first."""
    if top < 1:
        raise ValueError(f"top must be at least 1, got {top}")
    return df.nlargest(top, "views").reset_index(drop=True)


def shorten(title: str, limit: int = 34) -> str:
    """Trim long titles so the y-axis labels stay readable."""
    title = title.strip()
    return title if len(title) <= limit else title[: limit - 1].rstrip() + "..."


def build_figure(df: pd.DataFrame, top: int = DEFAULT_TOP):
    """Build the horizontal bar chart figure for the top-viewed videos."""
    data = top_by_views(df, top).copy()
    data["label"] = data["title"].map(shorten)

    fig = px.bar(
        data,
        x="views",
        y="label",
        color="category",
        orientation="h",
        title=f"Top {len(data)} trending videos by views",
        labels={"views": "Views", "label": "", "category": "Category"},
        hover_data={"channel": True, "likes": ":,", "comments": ":,", "label": False},
    )
    # nlargest gives us biggest-first; reversing the axis puts it at the top.
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        xaxis_tickformat=",",
        margin=dict(l=10, r=10, t=60, b=40),
        legend_title_text="Category",
    )
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP,
        help=f"how many videos to chart (default {DEFAULT_TOP})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="output HTML path (default output/top_videos.html)",
    )
    args = parser.parse_args()

    df = load_clean()
    fig = build_figure(df, args.top)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(args.output, include_plotlyjs="cdn")

    print(f"charted {min(args.top, len(df))} of {len(df)} videos")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
