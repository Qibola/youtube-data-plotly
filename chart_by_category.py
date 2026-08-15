"""Day 5 - aggregate by category: which topics pull the most, and which pull hardest.

Days 3 and 4 plot one dot or one bar per video. This one zooms out: group the
videos by category and ask two different questions at once.

  * bars  = total views for the category  ("how much reach does this topic have?")
  * dots  = like rate                     ("how hard does its audience engage?")

Those two answers live on very different scales - millions of views next to a
percentage - so the like rate gets its own axis on the right. The interesting
categories are the ones where the two disagree: a small category with a high
like rate has a more devoted audience than a big one with a low rate.

    python3 chart_by_category.py                 # -> output/by_category.html
    python3 chart_by_category.py --sort likes    # order bars by like rate instead
"""

import argparse
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from load_data import load_clean

OUTPUT_PATH = Path(__file__).parent / "output" / "by_category.html"

BAR_COLOR = "#4c78a8"
DOT_COLOR = "#e45756"


def summarise_categories(df: pd.DataFrame) -> pd.DataFrame:
    """One row per category, sorted by total views (most first).

    Columns: category, videos, total_views, avg_views, total_likes,
    total_comments, like_rate (likes as a percentage of that category's views).

    The like rate is computed from the category totals rather than by averaging
    each video's own rate - that way a tiny video with a freak 40% rate can't
    drag the whole category up with it.
    """
    grouped = (
        df.groupby("category")
        .agg(
            videos=("video_id", "count"),
            total_views=("views", "sum"),
            avg_views=("views", "mean"),
            total_likes=("likes", "sum"),
            total_comments=("comments", "sum"),
        )
        .reset_index()
    )

    grouped["avg_views"] = grouped["avg_views"].round(0).astype("int64")
    # Guard the divide: a category with no views gets a rate of 0, not NaN.
    grouped["like_rate"] = 0.0
    seen = grouped["total_views"] > 0
    grouped.loc[seen, "like_rate"] = (
        grouped.loc[seen, "total_likes"] / grouped.loc[seen, "total_views"] * 100
    ).round(2)

    return grouped.sort_values("total_views", ascending=False).reset_index(drop=True)


def build_figure(summary: pd.DataFrame, sort_by: str = "views") -> go.Figure:
    """Bars of total views per category, with like rate on a second y-axis."""
    key = "like_rate" if sort_by == "likes" else "total_views"
    data = summary.sort_values(key, ascending=False)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data["category"],
            y=data["total_views"],
            name="Total views",
            marker_color=BAR_COLOR,
            customdata=data[["videos", "avg_views", "total_likes"]],
            hovertemplate=(
                "Total views: %{y:,}<br>"
                "Videos: %{customdata[0]}<br>"
                "Average views: %{customdata[1]:,}<br>"
                "Total likes: %{customdata[2]:,}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["category"],
            y=data["like_rate"],
            name="Like rate",
            yaxis="y2",
            mode="markers+lines",
            line=dict(color=DOT_COLOR, width=2, dash="dot"),
            marker=dict(color=DOT_COLOR, size=13, line=dict(width=1, color="white")),
            hovertemplate="Like rate: %{y:.2f}%<extra></extra>",
        )
    )

    fig.update_layout(
        title="Reach vs engagement, by category",
        xaxis_title="Category",
        yaxis=dict(title="Total views", tickformat=","),
        yaxis2=dict(
            title="Like rate (%)",
            overlaying="y",
            side="right",
            showgrid=False,
            rangemode="tozero",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=10, r=10, t=90, b=40),
        hovermode="x unified",
    )
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--sort",
        choices=["views", "likes"],
        default="views",
        help="order the categories by total views (default) or by like rate",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="output HTML path (default output/by_category.html)",
    )
    args = parser.parse_args()

    summary = summarise_categories(load_clean())
    fig = build_figure(summary, sort_by=args.sort)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(args.output, include_plotlyjs="cdn")

    printable = summary[["category", "videos", "total_views", "avg_views", "like_rate"]]
    print(printable.to_string(index=False))
    best = summary.loc[summary["like_rate"].idxmax()]
    print(f"\nhighest like rate: {best['category']} at {best['like_rate']:.2f}%")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
