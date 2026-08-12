#!/usr/bin/env python3
"""
Extract the official NBA regular-season schedule from the league's
by-date PDF into a Basketball-Reference-compatible raw CSV.

Source (2026-27 example):
  https://pr.nba.com/wp-content/uploads/sites/46/2026/08/2026-27-NBA-Regular-Season-Schedule-By-Date.pdf

The PDF game index is not sequential; rows are sorted by date + ET time.
Team short names are expanded to the full names used by Basketball-Reference
and by the rest of this repo.

Output is written to data/nba/raw/nba_YYYY.csv (schedule-only: blank PTS).
Run data/process_nba_schedules.py afterwards to produce the slim processed file.

Requires: pdfplumber, pandas (optional)
  pip install pdfplumber
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path

try:
    import pdfplumber
except ImportError as e:
    raise SystemExit("pdfplumber is required: pip install pdfplumber") from e

SHORT_TO_FULL = {
    "Atlanta": "Atlanta Hawks",
    "Boston": "Boston Celtics",
    "Brooklyn": "Brooklyn Nets",
    "Charlotte": "Charlotte Hornets",
    "Chicago": "Chicago Bulls",
    "Cleveland": "Cleveland Cavaliers",
    "Dallas": "Dallas Mavericks",
    "Denver": "Denver Nuggets",
    "Detroit": "Detroit Pistons",
    "Golden State": "Golden State Warriors",
    "Houston": "Houston Rockets",
    "Indiana": "Indiana Pacers",
    "LA Clippers": "Los Angeles Clippers",
    "LA Lakers": "Los Angeles Lakers",
    "Memphis": "Memphis Grizzlies",
    "Miami": "Miami Heat",
    "Milwaukee": "Milwaukee Bucks",
    "Minnesota": "Minnesota Timberwolves",
    "New Orleans": "New Orleans Pelicans",
    "New York": "New York Knicks",
    "Oklahoma City": "Oklahoma City Thunder",
    "Orlando": "Orlando Magic",
    "Philadelphia": "Philadelphia 76ers",
    "Phoenix": "Phoenix Suns",
    "Portland": "Portland Trail Blazers",
    "Sacramento": "Sacramento Kings",
    "San Antonio": "San Antonio Spurs",
    "Toronto": "Toronto Raptors",
    "Utah": "Utah Jazz",
    "Washington": "Washington Wizards",
}

LINE_RE = re.compile(
    r"^(\d+)\s+"
    r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.\s+"
    r"(\d{1,2}/\d{1,2}/\d{2})\s+"
    r"(.+?)\s+(at|vs)\s+"
    r"(.+?)\s+"
    r"(\d{1,2}:\d{2}\s*[AP]M)\s+"
    r"(\d{1,2}:\d{2}\s*[AP]M)"
    r"(.*)$",
    re.MULTILINE | re.IGNORECASE,
)


def parse_et_to_br(et: str) -> str:
    m = re.match(r"(\d{1,2}):(\d{2})\s*([AP]M)", et.strip(), re.I)
    if not m:
        return et.strip().lower()
    h, mi, ap = int(m.group(1)), m.group(2), m.group(3).upper()
    return f"{h}:{mi}{ap[0].lower()}"


def date_to_br(day: str, date_str: str) -> str:
    dt = datetime.strptime(date_str, "%m/%d/%y")
    return f"{day} {dt.strftime('%b')} {dt.day} {dt.year}"


def extract(pdf_path: Path) -> list[dict]:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += (page.extract_text() or "") + "\n"

    matches = LINE_RE.findall(full_text)
    rows = []
    for m in matches:
        _gnum, day, datestr, team1, connector, team2, _local, et, rest = m
        t1 = SHORT_TO_FULL.get(team1.strip(), team1.strip())
        t2 = SHORT_TO_FULL.get(team2.strip(), team2.strip())
        if t1 not in SHORT_TO_FULL.values() or t2 not in SHORT_TO_FULL.values():
            print(f"WARNING: unmapped team(s): {team1!r} / {team2!r}")

        notes_parts = []
        if connector.lower() == "vs":
            notes_parts.append("Neutral")
        if re.search(r"\bC\b", rest):
            notes_parts.append("NBA Cup")
        notes = "; ".join(notes_parts)

        dt = datetime.strptime(datestr, "%m/%d/%y")
        tm = datetime.strptime(et.strip(), "%I:%M %p")
        rows.append(
            {
                "sort_key": (dt, tm.hour, tm.minute),
                "Date": date_to_br(day, datestr),
                "Start (ET)": parse_et_to_br(et),
                "Visitor/Neutral": t1,
                "Home/Neutral": t2,
                "Notes": notes,
            }
        )

    rows.sort(key=lambda r: r["sort_key"])
    return rows


def write_raw_csv(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "Date", "Start (ET)", "Visitor/Neutral", "PTS", "Home/Neutral", "PTS",
        "", "", "Attend.", "LOG", "Arena", "Notes",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([
                r["Date"], r["Start (ET)"], r["Visitor/Neutral"], "",
                r["Home/Neutral"], "", "", "", "", "", "", r["Notes"],
            ])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", type=Path, help="Path to the by-date schedule PDF")
    p.add_argument(
        "--season",
        type=int,
        required=True,
        help="Season end year (e.g. 2027 for 2026-27)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: data/nba/raw/nba_{season}.csv)",
    )
    args = p.parse_args()

    out = args.out or (
        Path(__file__).resolve().parent / "nba" / "raw" / f"nba_{args.season}.csv"
    )
    rows = extract(args.pdf)
    write_raw_csv(rows, out)
    print(f"Extracted {len(rows)} games -> {out}")


if __name__ == "__main__":
    main()
