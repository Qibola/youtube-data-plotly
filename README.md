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
| `publish_date` | ISO date in July 2026 |
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
is Day 2's job — the point is to practise it, not to avoid it.

## Roadmap

This project is built a small piece at a time. Progress:

- [x] Day 1 — Scaffold: README, requirements, synthetic `data/trending.csv` generator
- [ ] Day 2 — Load + clean the CSV with pandas (dedupe, fix dtypes, normalise categories)
- [ ] Day 3 — Bar chart: top videos by views, written to an interactive HTML file
- [ ] Day 4 — Scatter: views vs likes, with useful hover labels
- [ ] Day 5 — Aggregate by category (total views / average engagement)
- [ ] Day 6 — Combine the charts into one report HTML + polish

## Files

| File | Purpose |
| --- | --- |
| `make_sample_data.py` | Generates the synthetic `data/trending.csv` |
| `data/trending.csv` | The dataset the charts are built from |
| `requirements.txt` | pandas + plotly |
