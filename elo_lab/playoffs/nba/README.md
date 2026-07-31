# NBA Playoff Simulation (Multisport Elo Lab)

Minimal viable, truthful NBA playoff layer for the Multisport Elo Lab Monte Carlo engine.
Mirrors the structure and design of `elo_lab/playoffs/nfl/` and `elo_lab/playoffs/nhl/`.

## Scope (MVP)

- Qualification: top 6 in each conference auto-qualify
- Play-In Tournament for seeds 7–10:
  - 7 hosts 8 → winner = #7 seed
  - 9 hosts 10 → winner advances, loser eliminated
  - Loser of 7/8 hosts winner of 9/10 → winner = #8 seed
- Fixed 1–8 bracket (no reseeding): 1v8, 2v7, 3v6, 4v5
- All series best-of-7 with 2-2-1-1-1 home format
- Home-court advantage driven by seed / better regular-season record
- Win probability driven by final regular-season Elo + configurable home advantage

## Package Layout

```
nba/
├── __init__.py
├── models.py
├── seeding.py
├── simulation.py
├── adapter.py
├── workflow_hook.py
├── integration.py
└── README.md
```

## Quick Start

```python
from elo_lab.playoffs.nba import (
    TeamStanding,
    run_nba_playoff_from_standings,
    accumulate_playoff_probabilities,
)

standings = [...]          # List[TeamStanding]
result = run_nba_playoff_from_standings(
    standings=standings,
    home_advantage=55.0,
)

print(result.champion)
print(result.team_reached)
```

## Round names tracked

- Play-In
- First Round
- Conference Semifinals
- Conference Finals
- NBA Finals
- Champion

## Integration

Same pattern as NFL / NHL:

1. `extract_standings(standings_df, team_elo)`
2. `run_playoffs_after_season(...)`  (or the lower-level functions)
3. Accumulate `team_reached` across Monte Carlo seasons
4. Surface probabilities in the dashboard

## Design Decisions

- Identical package shape and public entry points as the other two sports.
- Play-In is fully simulated (three single-elimination games).
- Fixed bracket after Play-In matches current NBA rules.
- Best-of-7 series with correct home schedule.
- Ready for the same `simulate_with_playoffs.py` sport-dispatch wrapper.
