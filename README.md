# youtube-data-plotly

Interactive charts of "trending" YouTube videos, built with [pandas](https://pandas.pydata.org/)
and [Plotly](https://plotly.com/python/). The charts are written out as standalone HTML files
you can open in a browser — hover, zoom, and pan all work with no server running.

**There is no YouTube API call here.** The dataset is synthetic: `make_sample_data.py`
generates it from a fixed random seed, so everyone gets the same numbers and the project
works offline with no API key.

## Setup

```bash
pip install -r requirements.txt
```

## The data

`data/trending.csv` — 43 rows, 6 channels across 6 categories. One row per video:

| Column | Meaning |
| --- | --- |
| `video_id` | Unique-ish id (`vid001`, ...) |
| `title` | Video title |
| `channel` | Creator name |
| `category` | Gaming / Food / Education / Music / Travel / Tech |
| `publish_date` | ISO date, July–August 2026 |
| `views`, `likes`, `comments` | Engagement counts |
| `duration_sec` | Length in seconds |

Regenerate it any time with:

```bash
python3 make_sample_data.py
```

### It's messy on purpose

Real exports are never clean, so this one isn't either. The file contains a duplicate
row, one blank `likes` value, one `views` value written with thousands separators
(`"79,432"`, which makes pandas read the whole column as text), inconsistent category
casing (`MUSIC` vs `Music`), and a title padded with stray whitespace. Cleaning that up
is `load_data.py`'s job — the point is to practise it, not to avoid it.

```bash
python3 load_data.py   # prints a before/after summary of the cleaning
```

`load_data.load_clean()` is the single entry point the chart scripts use, so every
chart from Day 3 onwards works from the same tidy DataFrame.

## The charts

Each chart script writes a standalone HTML file into `output/` (git-ignored, since
it's regenerated). Open the file in a browser — Plotly's hover, zoom and pan all
work offline apart from loading plotly.js from a CDN.

### Top videos by views (Day 3)

```bash
python3 chart_top_videos.py             # top 10 -> output/top_videos.html
python3 chart_top_videos.py --top 5     # fewer bars
python3 chart_top_videos.py -o mine.html
```

A horizontal bar chart, most-viewed at the top, coloured by category. Titles are
shortened by `shorten()` so the axis labels stay readable, and hovering a bar shows
the channel plus like and comment counts. The chart-building logic lives in
`build_figure(df, top)`, which takes a DataFrame and returns a Plotly figure — so it
can be reused by the combined report on Day 6 without re-reading the CSV.

## Roadmap

This project is built a small piece at a time. Progress:

- [x] Day 1 — Scaffold: README, requirements, synthetic `data/trending.csv` generator
- [x] Day 2 — Load + clean the CSV with pandas (dedupe, fix dtypes, normalise categories)
- [x] Day 3 — Bar chart: top videos by views, written to an interactive HTML file
- [ ] Day 4 — Scatter: views vs likes, with useful hover labels
- [ ] Day 5 — Aggregate by category (total views / average engagement)
- [ ] Day 6 — Combine the charts into one report HTML + polish

## Files

| File | Purpose |
| --- | --- |
| `make_sample_data.py` | Generates the synthetic `data/trending.csv` |
| `load_data.py` | Loads + cleans the CSV; `load_clean()` returns the tidy DataFrame |
| `chart_top_videos.py` | Day 3 bar chart: top N videos by views |
| `data/trending.csv` | The dataset the charts are built from |
| `requirements.txt` | pandas + plotly |
