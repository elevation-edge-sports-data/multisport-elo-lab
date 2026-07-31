# NFL Playoff Simulation (Multisport Elo Lab)

Minimal viable, truthful NFL playoff layer for the Multisport Elo Lab Monte Carlo engine.

## Scope (MVP)

- Qualification: 4 division winners + 3 wild cards per conference
- Seeding: division winners = seeds 1–4 (by record), wild cards = seeds 5–7
- Wild Card: #1 seed bye; 2v7, 3v6, 4v5
- Reseeding after Wild Card and after Divisional (highest remaining seed always hosts lowest remaining seed)
- Single-elimination games only
- Win probability driven by final regular-season Elo + configurable home advantage
- Super Bowl treated as neutral site by default

Tiebreakers follow the accepted sequence defined in the project conversation.  
Any minor ordering discrepancy is treated as a low-priority quality item.

## Package Layout

```
nfl_playoffs/
├── __init__.py          # public API
├── models.py            # TeamStanding, GameResult, RoundResult, PlayoffResult
├── seeding.py           # seed_nfl_playoffs + basic tiebreaker helpers
├── simulation.py        # single-game sim + full bracket + reseeding
├── integration.py       # Monte Carlo probability accumulation example
└── README.md
```

## Quick Start

```python
from nfl_playoffs import (
    TeamStanding,
    run_nfl_playoff_from_standings,
    accumulate_playoff_probabilities,
)

# 1. After a regular-season simulation finishes you already have
#    a list of TeamStanding objects and an elo_lookup dict.

standings = [...]          # List[TeamStanding]
result = run_nfl_playoff_from_standings(
    standings=standings,
    home_advantage=55.0,   # pull from sport config
)

print(result.champion)
print(result.team_reached)

# 2. Across many Monte Carlo seasons
all_standings = [extract_standings(s) for s in monte_carlo_seasons]
probs = accumulate_playoff_probabilities(
    all_standings=all_standings,
    n_sims=len(all_standings),
)
# probs[team_id]["Champion"], probs[team_id]["Conference"], etc.
```

## Integration Points with Existing Lab

1. Extract `List[TeamStanding]` from the finished regular-season Monte Carlo result (wins, losses, win_pct, conference, division, final Elo).
2. Call `run_nfl_playoff_from_standings` (or the lower-level `seed_nfl_playoffs` + `simulate_nfl_playoffs`).
3. Accumulate the `team_reached` dictionaries across all simulations.
4. Surface the resulting probabilities in the Streamlit dashboard (new section or extra columns in the Season Simulation tab).

## Design Decisions

- No incremental maintenance of cumulative stats during the regular season unless profiling proves it is faster.
- All ranking / seeding work occurs once per completed season.
- Single-game simulation is extremely cheap relative to a full regular-season Monte Carlo.
- Home advantage and Super Bowl site logic are configurable so they can later be driven by the existing sport-config layer.
- The same package structure can later host parallel `nhl_playoffs` and `nba_playoffs` modules.

## Next Steps (after NFL is solid)

1. NHL fixed-bracket best-of-7 path
2. NBA (including Play-In tournament)
3. Richer / more granular data for advanced modeling variants
