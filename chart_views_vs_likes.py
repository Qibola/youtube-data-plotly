"""Day 4 - scatter plot of views vs likes.

A bar chart answers "which videos are biggest?". A scatter answers a more
interesting question: do views actually turn into likes? Each dot is one video,
so the shape of the cloud shows whether engagement scales with reach, and which
videos beat or miss the trend.

Extras that make the chart worth hovering over:

  * dot size = comment count, so busy comment sections stand out
  * colour   = category
  * hover    = full title, channel, exact counts, and a like rate (likes/views)
  * log axes, because view counts span several orders of magnitude and a linear
    axis squashes every smaller video into the corner

    python3 chart_views_vs_likes.py            # -> output/views_vs_likes.html
    python3 chart_views_vs_likes.py --linear   # linear axes instead of log
"""

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px

from load_data import load_clean

OUTPUT_PATH = Path(__file__).parent / "output" / "views_vs_likes.html"


def add_engagement(df: pd.DataFrame) -> pd.DataFrame:
    """Add a `like_rate` column: likes as a percentage of views.

    Videos with zero views would divide by zero, so those get a rate of 0.0.
    """
    data = df.copy()
    data["like_rate"] = 0.0
    has_views = data["views"] > 0
    data.loc[has_views, "like_rate"] = (
        data.loc[has_views, "likes"] / data.loc[has_views, "views"] * 100
    ).round(2)
    return data


def build_figure(df: pd.DataFrame, log_axes: bool = True):
    """Build the views-vs-likes scatter figure."""
    data = add_engagement(df)

    fig = px.scatter(
        data,
        x="views",
        y="likes",
        color="category",
        size="comments",
        size_max=34,
        log_x=log_axes,
        log_y=log_axes,
        title="Do views turn into likes?",
        labels={
            "views": "Views",
            "likes": "Likes",
            "category": "Category",
            "like_rate": "Like rate (%)",
            "comments": "Comments",
        },
        hover_name="title",
        hover_data={
            "channel": True,
            "views": ":,",
            "likes": ":,",
            "comments": ":,",
            "like_rate": ":.2f",
            "category": False,
        },
    )

    # A dot at 0 has nowhere to sit on a log axis, so say so rather than
    # silently dropping it.
    if log_axes and (data["likes"] <= 0).any():
        fig.add_annotation(
            text="Videos with 0 likes can't be shown on a log scale - rerun with --linear to see them.",
            xref="paper",
            yref="paper",
            x=0,
            y=1.06,
            showarrow=False,
            font=dict(size=11, color="#888888"),
        )

    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="white")))
    fig.update_layout(
        margin=dict(l=10, r=10, t=80, b=40),
        legend_title_text="Category",
    )
    if not log_axes:
        fig.update_layout(xaxis_tickformat=",", yaxis_tickformat=",")
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--linear",
        action="store_true",
        help="use linear axes instead of the default log scale",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="output HTML path (default output/views_vs_likes.html)",
    )
    args = parser.parse_args()

    df = load_clean()
    fig = build_figure(df, log_axes=not args.linear)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(args.output, include_plotlyjs="cdn")

    rates = add_engagement(df)["like_rate"]
    print(f"plotted {len(df)} videos ({'linear' if args.linear else 'log'} axes)")
    print(f"like rate: min {rates.min():.2f}%  median {rates.median():.2f}%  max {rates.max():.2f}%")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
