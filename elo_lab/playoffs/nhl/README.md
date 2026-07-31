# NHL Playoff Simulation (Multisport Elo Lab)

Minimal viable, truthful NHL playoff layer for the Multisport Elo Lab Monte Carlo engine.
Mirrors the structure and design of `elo_lab/playoffs/nfl/`.

## Scope (MVP)

- Qualification: top 3 in each division + 2 wild cards per conference
- Fixed bracket (no reseeding):
  - Best division winner vs lower wild card
  - Other division winner vs higher wild card
  - 2nd vs 3rd inside each division
- All series best-of-7 with 2-2-1-1-1 home format
- Home-ice advantage driven by original seed / better regular-season points
- Win probability driven by final regular-season Elo + configurable home advantage
- Stanley Cup Final uses the better regular-season Elo team as the higher seed (home ice)

## Package Layout

```
nhl/
├── __init__.py          # public API
├── models.py            # TeamStanding, GameResult, SeriesResult, RoundResult, PlayoffResult
├── seeding.py           # seed_nhl_playoffs + ranking helpers
├── simulation.py        # single-game + best-of-7 + fixed bracket
├── adapter.py           # extract_standings + NHL_TEAM_META
├── workflow_hook.py     # run_playoffs_after_season (drop-in for existing workflow)
├── integration.py       # Monte Carlo probability accumulation helper
└── README.md
```

## Quick Start

```python
from elo_lab.playoffs.nhl import (
    TeamStanding,
    run_nhl_playoff_from_standings,
    accumulate_playoff_probabilities,
)

# 1. After a regular-season simulation finishes
standings = [...]          # List[TeamStanding]
result = run_nhl_playoff_from_standings(
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
# probs[team_id]["Champion"], probs[team_id]["Stanley Cup Final"], etc.
```

## Integration Points with Existing Lab

1. Extract `List[TeamStanding]` from the finished regular-season Monte Carlo result
   (points, wins, losses, conference, division, final Elo).
2. Call `run_nhl_playoff_from_standings` (or the lower-level `seed_nhl_playoffs` + `simulate_nhl_playoffs`).
3. Accumulate the `team_reached` dictionaries across all simulations.
4. Surface the resulting probabilities in the Streamlit dashboard.

## Design Decisions

- Same package shape and public entry points as the NFL module for easy multi-sport orchestration.
- Fixed bracket (no reseeding) matches the current NHL format.
- Best-of-7 series with correct 2-2-1-1-1 home schedule.
- Ranking uses points first, then regulation wins / win_pct (NHL-aware).
- Home advantage and Final home-ice logic are configurable.
- Ready for the same workflow_hook / simulate_with_playoffs wrapper pattern used by NFL.

## Next Steps

1. Wire into `simulate_with_playoffs.py` (sport dispatch).
2. Surface “First Round / Second Round / Conference Finals / Stanley Cup / Champion” probabilities in the dashboard.
3. NBA module (Play-In + fixed 1–8 bracket).
