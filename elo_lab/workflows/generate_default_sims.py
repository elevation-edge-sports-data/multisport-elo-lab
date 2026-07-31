#!/usr/bin/env python3
"""
elo_lab/workflows/generate_default_sims.py

One-time (or CI) workflow that runs the default Monte Carlo simulation
for NHL, NBA and NFL and writes the results to data/precomputed/.

Usage (from repo root):

    python -m elo_lab.workflows.generate_default_sims

    # optional overrides
    python -m elo_lab.workflows.generate_default_sims --n-sims 300 --sports NHL NBA

    # or as a plain script
    python elo_lab/workflows/generate_default_sims.py
"""

from __future__ import annotations

import argparse
import pickle
import sys
import time
from pathlib import Path


# ---------------------------------------------------------------------------
# Locate the repository root reliably whether we are run as:
#   python -m elo_lab.workflows.generate_default_sims
#   python elo_lab/workflows/generate_default_sims.py
# ---------------------------------------------------------------------------
def _find_repo_root() -> Path:
    """Walk upward from this file until we find a directory that contains
    both 'elo_lab' and 'app' (or 'data')."""
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "elo_lab").is_dir() and (
            (candidate / "app").is_dir() or (candidate / "data").is_dir()
        ):
            return candidate
    # Fallback: three levels up from workflows/ (elo_lab/workflows → repo root)
    return here.parents[2]


ROOT = _find_repo_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Streamlit / project bootstrap (sets up paths the same way the dashboard does)
try:
    import bootstrap  # noqa: F401
except ImportError:
    pass

from app.services.simulation_service import run_simulation
from app.services.initial_ratings_service import (
    get_available_seasons,
    get_initial_ratings,
)


# ---------------------------------------------------------------------------
# Default model config (mirrors the dashboard defaults)
# ---------------------------------------------------------------------------
def default_config() -> dict:
    """
    Matches the sidebar defaults:
      - Home advantage ON  (55 Elo points)
      - Margin of victory ON (scale 1.0)
      - Elevation Edge OFF
      - k-factor = 20
    """
    return {
        "k": 20,
        "adjustments": {
            "home_field": {"enabled": True, "value": 55},
            "margin_of_victory": {"enabled": True, "scale": 1.0},
            # elevation_edge intentionally omitted (disabled by default)
        },
    }


def _schedule_path(sport: str) -> str:
    mapping = {
        "NHL": "data/nhl_games.csv",
        "NFL": "data/nfl_games.csv",
        "NBA": "data/nba_games.csv",
    }
    return mapping.get(sport, f"data/{sport.lower()}_games.csv")


def generate_one(sport: str, n_sims: int, out_dir: Path) -> Path:
    print(f"\n{'=' * 60}")
    print(f"  Generating default simulation for {sport}  (n_sims={n_sims})")
    print(f"{'=' * 60}")

    config = default_config()
    schedule_path = _schedule_path(sport)

    # Use the most recent available season if possible
    seasons = get_available_seasons(sport)
    season = seasons[-1] if seasons else None
    print(f"  Season          : {season or '(all / latest)'}")
    print(f"  Schedule path   : {schedule_path}")

    initial_ratings = get_initial_ratings(
        sport=sport,
        schedule_path=schedule_path,
        season=season,
        rating_source="playoffs",
        rating_basis="record",
        apply_regression=False,
    )
    print(f"  Initial ratings : {len(initial_ratings)} teams")

    t0 = time.perf_counter()
    results = run_simulation(
        config=config,
        n_sims=n_sims,
        initial_ratings=initial_ratings,
        sport=sport,
        season=season,
    )
    elapsed = time.perf_counter() - t0
    print(f"  Finished in {elapsed:.1f}s")

    # Light sanity checks
    summary = results.get("summary")
    playoff = results.get("playoff_probs", {})
    print(f"  Summary rows    : {len(summary) if summary is not None else 0}")
    print(f"  Playoff teams   : {len(playoff)}")

    out_path = out_dir / f"{sport}_default.pkl"
    with open(out_path, "wb") as f:
        pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)

    size_kb = out_path.stat().st_size / 1024
    print(f"  Wrote {out_path}  ({size_kb:.1f} KB)")
    return out_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate default precomputed simulations for Multisport Elo Lab"
    )
    parser.add_argument(
        "--n-sims",
        type=int,
        default=250,
        help="Number of Monte Carlo seasons (default 250 – good balance of speed vs stability)",
    )
    parser.add_argument(
        "--sports",
        nargs="+",
        default=["NHL", "NBA", "NFL"],
        choices=["NHL", "NBA", "NFL"],
        help="Sports to generate (default: all three)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory for the .pkl files (default: <repo>/data/precomputed)",
    )
    args = parser.parse_args(argv)

    out_dir = args.out_dir or (ROOT / "data" / "precomputed")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {out_dir.resolve()}")

    written = []
    for sport in args.sports:
        path = generate_one(sport, args.n_sims, out_dir)
        written.append(path)

    print(f"\nDone. Generated {len(written)} file(s):")
    for p in written:
        print(f"  • {p}")


if __name__ == "__main__":
    main()
