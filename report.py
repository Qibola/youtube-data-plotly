"""Day 6 - stitch the three charts into one standalone report page.

Days 3, 4 and 5 each write their own HTML file. That's three tabs to open and
no story tying them together. This script builds one page instead: a few
headline numbers at the top, then all three charts stacked with a sentence of
context above each.

The trick that makes it work is `fig.to_html(full_html=False)`, which returns
just the `<div>` for a chart rather than a whole document. Plotly's JS library
only needs to be loaded once for the page, so the first chart is written with
`include_plotlyjs="cdn"` and the rest with `include_plotlyjs=False` - otherwise
the same 3MB library gets pulled in three times.

Every figure comes from the existing `build_figure()` functions, so there is no
chart code duplicated here. The data is read once and passed to all three.

    python3 report.py                  # -> output/report.html
    python3 report.py --top 5          # fewer bars in the first chart
    python3 report.py -o ~/report.html
"""

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

import chart_by_category
import chart_top_videos
import chart_views_vs_likes
from load_data import load_clean

OUTPUT_PATH = Path(__file__).parent / "output" / "report.html"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trending video report</title>
<style>
  :root {{ color-scheme: light; }}
  body {{
    margin: 0;
    padding: 2rem 1rem 4rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    color: #22272e;
    background: #f6f7f9;
  }}
  main {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ margin: 0 0 .25rem; font-size: 1.9rem; }}
  .subtitle {{ margin: 0 0 2rem; color: #6b7280; }}
  .stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 2.5rem;
  }}
  .stat {{
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1rem;
  }}
  .stat .value {{ font-size: 1.5rem; font-weight: 600; }}
  .stat .label {{ font-size: .8rem; color: #6b7280; text-transform: uppercase; letter-spacing: .04em; }}
  section {{
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 2rem;
  }}
  section p {{ margin: 0 0 1rem; color: #4b5563; line-height: 1.5; }}
  footer {{ color: #9ca3af; font-size: .85rem; text-align: center; }}
</style>
</head>
<body>
<main>
  <h1>Trending video report</h1>
  <p class="subtitle">Synthetic dataset &middot; generated {generated}</p>
  <div class="stats">{stats}</div>
  {sections}
  <footer>Built with pandas + Plotly. Hover, zoom and pan all work offline.</footer>
</main>
</body>
</html>
"""


def headline_stats(df: pd.DataFrame) -> list[tuple[str, str]]:
    """A handful of (label, value) pairs to sit above the charts."""
    total_views = int(df["views"].sum())
    total_likes = int(df["likes"].sum())
    like_rate = total_likes / total_views * 100 if total_views else 0.0
    top = df.loc[df["views"].idxmax()]
    busiest = df.groupby("category")["views"].sum().idxmax()

    return [
        ("Videos", f"{len(df):,}"),
        ("Total views", f"{total_views:,}"),
        ("Overall like rate", f"{like_rate:.2f}%"),
        ("Biggest video", chart_top_videos.shorten(top["title"], 28)),
        ("Biggest category", busiest),
    ]


def render_stats(stats: list[tuple[str, str]]) -> str:
    return "".join(
        f'<div class="stat"><div class="value">{value}</div>'
        f'<div class="label">{label}</div></div>'
        for label, value in stats
    )


def build_sections(df: pd.DataFrame, top: int) -> str:
    """Render each figure as a `<div>` and wrap it with a line of context.

    Only the first chart carries the Plotly library; the others reuse it.
    """
    blurbs = [
        (
            chart_top_videos.build_figure(df, top),
            "Which videos pulled the most views. Bars are coloured by category, "
            "so you can see at a glance whether one topic owns the top of the list.",
        ),
        (
            chart_views_vs_likes.build_figure(df),
            "One dot per video, views across and likes up. The cloud slopes up to "
            "the right because reach brings likes with it - the dots sitting above "
            "or below that trend are the interesting ones. Both axes are logarithmic.",
        ),
        (
            chart_by_category.build_figure(chart_by_category.summarise_categories(df)),
            "Zoomed out to categories: bars are total views, dots are like rate on "
            "the right-hand axis. Look for the categories where the two disagree.",
        ),
    ]

    parts = []
    for index, (fig, blurb) in enumerate(blurbs):
        # The library only needs to land on the page once.
        plotlyjs = "cdn" if index == 0 else False
        div = fig.to_html(full_html=False, include_plotlyjs=plotlyjs)
        parts.append(f"<section><p>{blurb}</p>{div}</section>")
    return "\n".join(parts)


def build_report(df: pd.DataFrame, top: int = chart_top_videos.DEFAULT_TOP) -> str:
    """Return the complete HTML document as a string."""
    return PAGE_TEMPLATE.format(
        generated=date.today().isoformat(),
        stats=render_stats(headline_stats(df)),
        sections=build_sections(df, top),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--top",
        type=int,
        default=chart_top_videos.DEFAULT_TOP,
        help=f"how many videos in the bar chart (default {chart_top_videos.DEFAULT_TOP})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="output HTML path (default output/report.html)",
    )
    args = parser.parse_args()

    df = load_clean()
    html = build_report(df, args.top)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(f"3 charts, {len(df)} videos -> {args.output}")
    print(f"{args.output.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
