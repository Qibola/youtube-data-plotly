"""Generate the synthetic trending dataset used by this project.

There is no YouTube API call here — the data is invented, but shaped like a real
"trending videos" export so the pandas/Plotly work later is realistic.

The output is deliberately a little messy (duplicate row, blank values,
inconsistent category casing, thousands separators in a numeric column). Cleaning
that up is Day 2's job.

Run:  python3 make_sample_data.py
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).parent / "data" / "trending.csv"

FIELDS = [
    "video_id",
    "title",
    "channel",
    "category",
    "publish_date",
    "views",
    "likes",
    "comments",
    "duration_sec",
]

# (channel, category, [titles]) — a handful of plausible creators per category.
SOURCES = [
    ("PixelForge", "Gaming", [
        "I Built a City Entirely Underwater",
        "Beating the Game Without Jumping",
        "Every Secret Level, Ranked",
    
        "A Speedrun Where Everything Goes Wrong",
        "Reviewing the Worst-Rated Game of the Year",
        "I Let Chat Design My Character",
        "The Boss Nobody Has Beaten Legitimately",
    ]),
    ("The Sunday Kitchen", "Food", [
        "One-Pan Dinners That Actually Work",
        "I Tested 7 Pizza Doughs",
        "The Only Soup Recipe You Need",
    
        "Feeding Six People for the Price of Two",
        "Every Egg Method, Tested",
        "The Bread I Make Every Single Week",
        "What Restaurants Do That You Can Copy",
    ]),
    ("Groundwork Science", "Education", [
        "Why Bridges Don't Fall Down",
        "The Math Behind Traffic Jams",
        "How Batteries Actually Store Energy",
    
        "The Hidden Cost of Cheap Concrete",
        "Why Your Wifi Dies in One Room",
        "How We Measure Things Too Big to Measure",
        "Everything Wrong With the Water Cycle Diagram",
    ]),
    ("Lo-Fi Attic", "Music", [
        "Rain, Coffee, and a Cheap Piano",
        "Late Night Study Set (1 Hour)",
        "Three Chords, One Take",
    
        "Slow Morning, Warm Tape",
        "A Loop I Could Not Stop Making",
        "Practice Session, Unedited",
        "Something Quiet for the Drive Home",
    ]),
    ("Trail Notes", "Travel", [
        "48 Hours in a Town With No Cars",
        "I Walked the Whole Coast Path",
        "Cheapest Way to Cross a Country",
    
        "The Trail That Almost Beat Me",
        "Sleeping Rough in a Storm",
        "Ten Days, One Backpack",
        "The Village at the End of the Line",
    ]),
    ("Deskbound", "Tech", [
        "This $40 Keyboard Beat My $200 One",
        "My Entire Setup Runs on One Cable",
        "A Week With No Notifications",
    
        "Every Cable I Own, Explained",
        "I Replaced My Laptop With a Phone",
        "The Case for a Slower Computer",
        "Three Years With the Same Mouse",
    ]),
]


def main() -> None:
    rng = random.Random(20260811)  # seeded → same CSV every run
    start = date(2026, 7, 1)
    rows = []
    n = 0

    for channel, category, titles in SOURCES:
        for title in titles:
            n += 1
            views = rng.randint(20_000, 2_400_000)
            # Like/comment rates vary by category but track views, so the
            # views-vs-likes scatter on Day 4 shows a real correlation.
            like_rate = rng.uniform(0.02, 0.075)
            likes = int(views * like_rate)
            comments = int(likes * rng.uniform(0.03, 0.14))

            rows.append({
                "video_id": f"vid{n:03d}",
                "title": title,
                "channel": channel,
                # Inconsistent casing on purpose — Day 2 normalises it.
                "category": category.upper() if n % 5 == 0 else category,
                "publish_date": (start + timedelta(days=rng.randint(0, 40))).isoformat(),
                "views": views,
                "likes": likes,
                "comments": comments,
                "duration_sec": rng.choice([94, 212, 348, 495, 612, 1080, 3600]),
            })

    rng.shuffle(rows)

    # --- deliberate mess for Day 2 to clean up ---
    rows.append(dict(rows[3]))                     # exact duplicate row
    rows[7]["likes"] = ""                          # missing value
    rows[11]["views"] = f'{rows[11]["views"]:,}'   # "1,234,567" instead of an int
    rows[2]["title"] = f'  {rows[2]["title"]}  '   # stray whitespace

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows to {OUT.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
