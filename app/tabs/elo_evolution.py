"""
Regular Season Projections tab.

Two-chart layout:
  1. Observed trajectory from the most recent completed season (top)
  2. Simulated trajectory for the target season (bottom)

Primary metric: cumulative wins (NFL / NBA) or points (NHL).
x-axis: games played.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from metadata import load_teams, NFL_TEAMS, NHL_TEAMS, NBA_TEAMS
except ImportError:
    from metadata.nfl_teams import NFL_TEAMS
    from metadata.nhl_teams import NHL_TEAMS
    try:
        from metadata.nba_teams import NBA_TEAMS
    except ImportError:
        NBA_TEAMS = {}

    def load_teams(sport):
        return {"NFL": NFL_TEAMS, "NHL": NHL_TEAMS, "NBA": NBA_TEAMS}.get(sport, {})

try:
    from components.logos import render_logo_strip
except ImportError:
    def render_logo_strip(*args, **kwargs):
        pass


# Fallback focus lists: Western (NHL/NBA) and AFC (NFL)
DEFAULT_FOCUS = {
    "NBA": ["OKC", "DEN", "MIN", "LAL", "GSW", "LAC"],
    "NHL": ["COL", "VGK", "DAL", "MIN", "EDM", "WPG"],
    "NFL": ["BUF", "KC", "BAL", "CIN", "HOU", "LAC"],
}

# Conference used for default team selection on this tab
DEFAULT_CONFERENCE = {
    "NBA": "Western",
    "NHL": "Western",
    "NFL": "AFC",
}

METRIC_LABEL = {
    "NHL": ("points", "Points"),
    "NBA": ("wins", "Wins"),
    "NFL": ("wins", "Wins"),
}


def get_team_color_map(sport: str) -> Dict[str, str]:
    try:
        teams = load_teams(sport)
    except Exception:
        teams = (
            NHL_TEAMS if sport == "NHL"
            else NBA_TEAMS if sport == "NBA"
            else NFL_TEAMS
        )
    color_map: Dict[str, str] = {}
    for abbr, data in teams.items():
        color = data.get("primary_color", "#888888")
        color_map[abbr] = color
        color_map[data.get("name", abbr)] = color
    return color_map


def hex_to_rgba(hex_color: str, alpha: float = 0.15) -> str:
    hex_color = (hex_color or "#888888").lstrip("#")
    if len(hex_color) != 6:
        return f"rgba(128, 128, 128, {alpha})"
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


def _name_maps(sport: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    try:
        teams = load_teams(sport)
    except Exception:
        teams = {}
    to_abbr: Dict[str, str] = {}
    to_name: Dict[str, str] = {}
    for abbr, data in teams.items():
        to_abbr[abbr] = abbr
        to_abbr[abbr.upper()] = abbr
        name = data.get("name", abbr)
        to_abbr[name] = abbr
        to_abbr[name.lower()] = abbr
        to_abbr[name.replace(".", "").lower()] = abbr
        to_name[abbr] = name
    return to_abbr, to_name


def _normalize_team(raw: str, to_abbr: Dict[str, str]) -> str:
    s = str(raw).strip()
    if s in to_abbr:
        return to_abbr[s]
    if s.upper() in to_abbr:
        return to_abbr[s.upper()]
    if s.lower() in to_abbr:
        return to_abbr[s.lower()]
    return s


def _load_season_schedule(sport: str, season: str) -> Optional[pd.DataFrame]:
    sport_l = sport.lower()
    candidates = [
        Path(f"data/{sport_l}/{sport_l}_{season}.csv"),
        Path(f"data/{sport_l}/{season}.csv"),
    ]
    for path in candidates:
        if path.is_file():
            try:
                return pd.read_csv(path)
            except Exception:
                continue
    return None


def _games_from_schedule(df: pd.DataFrame, sport: str) -> pd.DataFrame:
    cols = {c.lower().strip(): c for c in df.columns}
    to_abbr, _ = _name_maps(sport)

    def col(*names):
        for n in names:
            if n.lower() in cols:
                return cols[n.lower()]
        return None

    if col("home_team") and col("away_team"):
        hs_c = col("home_score", "home_pts", "pts_home")
        as_c = col("away_score", "away_pts", "pts_away")
        out = pd.DataFrame({
            "home": df[col("home_team")].map(lambda x: _normalize_team(x, to_abbr)),
            "away": df[col("away_team")].map(lambda x: _normalize_team(x, to_abbr)),
            "home_score": pd.to_numeric(df[hs_c], errors="coerce") if hs_c else pd.NA,
            "away_score": pd.to_numeric(df[as_c], errors="coerce") if as_c else pd.NA,
        })
        out["order"] = range(len(out))
        return out.dropna(subset=["home", "away"])

    winner_c = col("winner/tie", "winner")
    loser_c = col("loser/tie", "loser")
    if winner_c and loser_c:
        marker_c = None
        win_idx = list(df.columns).index(winner_c)
        if win_idx + 1 < len(df.columns):
            maybe = df.columns[win_idx + 1]
            if maybe != loser_c:
                marker_c = maybe
        rows = []
        pts_cols = [c for c in df.columns if str(c).lower().startswith("pts")]
        for _, row in df.iterrows():
            w = str(row[winner_c]).strip()
            l = str(row[loser_c]).strip()
            if not w or not l or w.lower() == "nan":
                continue
            at_home_loss = False
            if marker_c is not None:
                at_home_loss = str(row[marker_c]).strip() == "@"
            home = l if at_home_loss else w
            away = w if at_home_loss else l
            hs = as_ = None
            if len(pts_cols) >= 2:
                try:
                    pw, pl = float(row[pts_cols[0]]), float(row[pts_cols[1]])
                    hs, as_ = (pl, pw) if at_home_loss else (pw, pl)
                except Exception:
                    pass
            rows.append({
                "home": _normalize_team(home, to_abbr),
                "away": _normalize_team(away, to_abbr),
                "home_score": hs,
                "away_score": as_,
                "order": len(rows),
            })
        return pd.DataFrame(rows)

    vis_c = col("visitor", "visitor/neutral", "away")
    home_c = col("home", "home/neutral")
    if vis_c and home_c:
        vis_idx = list(df.columns).index(vis_c)
        home_idx = list(df.columns).index(home_c)
        v_score_c = df.columns[vis_idx + 1] if vis_idx + 1 < len(df.columns) else None
        h_score_c = df.columns[home_idx + 1] if home_idx + 1 < len(df.columns) else None
        rows = []
        for _, row in df.iterrows():
            away = str(row[vis_c]).strip()
            home = str(row[home_c]).strip()
            if not away or not home or away.lower() == "nan":
                continue
            try:
                as_ = float(row[v_score_c]) if v_score_c is not None else None
                hs = float(row[h_score_c]) if h_score_c is not None else None
            except Exception:
                as_ = hs = None
            rows.append({
                "home": _normalize_team(home, to_abbr),
                "away": _normalize_team(away, to_abbr),
                "home_score": hs,
                "away_score": as_,
                "order": len(rows),
            })
        return pd.DataFrame(rows)

    return pd.DataFrame(columns=["home", "away", "home_score", "away_score", "order"])


def build_observed_trajectory(sport: str, season: str) -> pd.DataFrame:
    df = _load_season_schedule(sport, season)
    if df is None or df.empty:
        return pd.DataFrame(columns=["team", "games_played", "value", "rank"])

    games = _games_from_schedule(df, sport)
    if games.empty:
        return pd.DataFrame(columns=["team", "games_played", "value", "rank"])

    played = games.dropna(subset=["home_score", "away_score"])
    if played.empty:
        return pd.DataFrame(columns=["team", "games_played", "value", "rank"])

    metric_key, _ = METRIC_LABEL.get(sport, ("wins", "Wins"))
    totals: Dict[str, float] = {}
    gp: Dict[str, int] = {}
    rows = []

    for _, g in played.sort_values("order").iterrows():
        home, away = g["home"], g["away"]
        hs, as_ = float(g["home_score"]), float(g["away_score"])
        for t in (home, away):
            totals.setdefault(t, 0.0)
            gp.setdefault(t, 0)

        if metric_key == "points":
            if hs > as_:
                totals[home] += 2
            elif as_ > hs:
                totals[away] += 2
            else:
                totals[home] += 1
                totals[away] += 1
        else:
            if hs > as_:
                totals[home] += 1
            elif as_ > hs:
                totals[away] += 1

        gp[home] += 1
        gp[away] += 1

        active = {t: totals[t] for t in totals if gp[t] > 0}
        ranked = sorted(active.keys(), key=lambda t: (-active[t], t))
        rank_map = {t: i + 1 for i, t in enumerate(ranked)}

        for t in (home, away):
            rows.append({
                "team": t,
                "games_played": gp[t],
                "value": totals[t],
                "rank": rank_map.get(t, len(ranked)),
            })

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return (
        out.sort_values(["team", "games_played"])
        .groupby(["team", "games_played"], as_index=False)
        .last()
    )


def _prior_season_label(sport: str, target: Optional[str]) -> Optional[str]:
    try:
        from services.initial_ratings_service import get_available_seasons
    except ImportError:
        return None
    seasons = get_available_seasons(sport)
    if not seasons:
        return None
    if target and target in seasons:
        idx = seasons.index(target)
        return seasons[idx - 1] if idx > 0 else None
    return seasons[-2] if len(seasons) >= 2 else seasons[-1]


def _make_trajectory_figure(
    df: pd.DataFrame,
    teams: List[str],
    color_map: Dict[str, str],
    y_col: str,
    y_label: str,
    title: str,
    band_low: Optional[str] = None,
    band_high: Optional[str] = None,
    reverse_y: bool = False,
) -> go.Figure:
    fig = go.Figure()
    x_col = "games_played"

    for team in teams:
        td = df[df["team"] == team].sort_values(x_col)
        if td.empty:
            continue
        color = color_map.get(team, "#666666")

        if band_low and band_high and band_low in td.columns and band_high in td.columns:
            fig.add_trace(go.Scatter(
                x=td[x_col], y=td[band_high],
                mode="lines", line=dict(width=0),
                showlegend=False, hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=td[x_col], y=td[band_low],
                mode="lines", line=dict(width=0),
                fill="tonexty",
                fillcolor=hex_to_rgba(color, 0.14),
                showlegend=False, hoverinfo="skip",
            ))

        fig.add_trace(go.Scatter(
            x=td[x_col],
            y=td[y_col],
            mode="lines",
            name=team,
            line=dict(width=2.6, color=color),
            hovertemplate=f"{team}<br>GP=%{{x}}<br>{y_label}=%{{y:.1f}}<extra></extra>",
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Games Played",
        yaxis_title=y_label,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=40, r=20, t=60, b=40),
        height=380,
    )
    if reverse_y:
        fig.update_yaxes(autorange="reversed")
    return fig



def _conference_team_set(sport: str, conference: str) -> set:
    """Abbreviations belonging to the given conference."""
    try:
        teams = load_teams(sport)
    except Exception:
        teams = {}
    return {
        abbr
        for abbr, meta in teams.items()
        if (meta or {}).get("conference") == conference
    }


def _default_teams_from_playoff_probs(
    sport: str,
    all_teams: List[str],
    results: dict,
    preferred: List[str],
    n: int = 6,
) -> List[str]:
    """
    Top n teams by probability of reaching the first true playoff round,
    restricted to the sport's focus conference (Western for NHL/NBA, AFC for NFL).
    NHL/NBA: First Round. NFL: Wild Card (or Make Playoffs).
    NBA: ignore Play-In when a First Round column exists.
    """
    playoff = results.get("playoff_probs") or {}
    achievement = results.get("achievement_probs")
    scores = {}
    conf = DEFAULT_CONFERENCE.get(sport)
    conf_teams = _conference_team_set(sport, conf) if conf else set()

    def _pick_round_value(payload: dict) -> float | None:
        if not isinstance(payload, dict):
            return None
        # Priority order by sport
        if sport == "NFL":
            keys = [
                "Wild Card", "Reach Wild Card", "wild_card",
                "Make Playoffs", "make_playoffs", "playoffs",
                "Divisional", "Conference", "Super Bowl", "Champion",
            ]
        elif sport == "NBA":
            keys = [
                "First Round", "Reach First Round", "first_round",
                "Conference Semifinals", "Conference Finals", "NBA Finals", "Champion",
            ]
        else:  # NHL
            keys = [
                "First Round", "Reach First Round", "first_round",
                "Second Round", "Conference Finals", "Stanley Cup Final", "Champion",
            ]
        for k in keys:
            if k in payload:
                try:
                    return float(payload[k])
                except (TypeError, ValueError):
                    continue
        # any numeric non-play-in key
        for k, v in payload.items():
            kl = str(k).lower().replace(" ", "")
            if "play-in" in kl or "playin" in kl:
                continue
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
        return None

    if isinstance(playoff, dict) and playoff:
        for team, payload in playoff.items():
            if team not in all_teams:
                continue
            if conf_teams and team not in conf_teams:
                continue
            val = _pick_round_value(payload)
            if val is not None:
                scores[team] = val

    if not scores and achievement is not None:
        try:
            adf = achievement if isinstance(achievement, pd.DataFrame) else pd.DataFrame(achievement)
            team_col = "team" if "team" in adf.columns else None
            if team_col:
                prefer = []
                for c in adf.columns:
                    cl = str(c).lower()
                    if c == team_col:
                        continue
                    if sport == "NBA" and ("play-in" in cl or "playin" in cl.replace(" ", "")):
                        continue
                    if "first" in cl or "wild" in cl or "make_playoff" in cl or "playoff" in cl:
                        prefer.append(c)
                col = prefer[0] if prefer else None
                if col:
                    for _, row in adf.iterrows():
                        team = str(row[team_col])
                        if team in all_teams and (not conf_teams or team in conf_teams):
                            try:
                                scores[team] = float(row[col])
                            except (TypeError, ValueError):
                                pass
        except Exception:
            pass

    if scores:
        ranked = sorted(scores.keys(), key=lambda tm: (-scores[tm], tm))
        picked = [tm for tm in ranked if tm in all_teams][:n]
        if len(picked) >= min(n, len(all_teams)):
            return picked
        # fill remaining from preferred
        for tm in preferred:
            if tm in all_teams and tm not in picked:
                picked.append(tm)
            if len(picked) >= n:
                break
        return picked[:n]

    fallback = [tm for tm in preferred if tm in all_teams]
    return (fallback or all_teams)[:n]


def render_elo_evolution_tab(sport: str = "NFL"):
    st.header(f"{sport} Regular Season Projections")

    metric_key, metric_label = METRIC_LABEL.get(sport, ("wins", "Wins"))
    color_map = get_team_color_map(sport)

    target_season = st.session_state.get("season")
    observed_season = _prior_season_label(sport, target_season)

    observed = (
        build_observed_trajectory(sport, observed_season)
        if observed_season
        else pd.DataFrame()
    )

    results = st.session_state.get("simulation_results") or {}
    evolution = results.get("elo_evolution", pd.DataFrame())
    if evolution is None:
        evolution = pd.DataFrame()

    sim_metric_mean = f"mean_{metric_key}"
    sim_metric_lo = f"p05_{metric_key}"
    sim_metric_hi = f"p95_{metric_key}"
    has_sim_metric = (not evolution.empty and sim_metric_mean in evolution.columns)

    if has_sim_metric:
        all_teams = sorted(evolution["team"].unique().tolist())
    elif not observed.empty:
        all_teams = sorted(observed["team"].unique().tolist())
    else:
        all_teams = []

    if not all_teams:
        st.info(
            "No projection data yet. Run a simulation from the sidebar, "
            "or ensure schedule files are available for observed paths."
        )
        return

    preferred = DEFAULT_FOCUS.get(sport, [])
    default_teams = _default_teams_from_playoff_probs(
        sport, all_teams, results, preferred
    )

    # Fingerprint forces multiselect defaults to refresh when results change
    fp = st.session_state.get("_results_fingerprint", "default")
    selected_teams = st.multiselect(
        "Select teams",
        options=all_teams,
        default=default_teams,
        help="Defaults to the top 6 teams in the focus conference "
             "(Western for NHL/NBA, AFC for NFL) by first-round / wild-card probability.",
        key=f"reg_season_proj_teams_{sport}_{fp}",
    )

    if not selected_teams:
        st.info("Select at least one team.")
        return

    logo_cols = st.columns([6, 2])
    with logo_cols[1]:
        render_logo_strip(sport, selected_teams, width=32, max_show=10)

    view_mode = st.radio(
        "Metric",
        options=[metric_label, "Standings rank"],
        horizontal=True,
        key=f"reg_season_metric_{sport}",
        help="Wins/points accumulate through the season. "
             "Standings rank is 1 = best (axis reversed).",
    )
    use_rank = view_mode == "Standings rank"

    st.subheader(f"Observed — {observed_season}" if observed_season else "Observed")
    if observed.empty:
        st.caption(
            f"No completed-season results available to plot an observed path for {sport}."
        )
    else:
        obs = observed[observed["team"].isin(selected_teams)]
        if use_rank:
            fig_obs = _make_trajectory_figure(
                obs, selected_teams, color_map,
                y_col="rank", y_label="Standings rank",
                title=f"Observed standings rank ({observed_season})",
                reverse_y=True,
            )
        else:
            fig_obs = _make_trajectory_figure(
                obs, selected_teams, color_map,
                y_col="value", y_label=metric_label,
                title=f"Observed {metric_label.lower()} ({observed_season})",
            )
        st.plotly_chart(fig_obs, use_container_width=True)

    st.subheader(f"Simulated — {target_season}" if target_season else "Simulated")
    if not has_sim_metric:
        st.caption(
            "Run a simulation to see projected trajectories for the target season. "
            "Simulated paths use the current model and Simulate from window."
        )
        if not evolution.empty and "mean_elo" in evolution.columns:
            st.caption("Rating path shown as interim view until win paths are generated.")
            filt = evolution[evolution["team"].isin(selected_teams)]
            fig_fb = _make_trajectory_figure(
                filt, selected_teams, color_map,
                y_col="mean_elo", y_label="Rating",
                title="Simulated rating (interim)",
                band_low="p05_elo" if "p05_elo" in filt.columns else None,
                band_high="p95_elo" if "p95_elo" in filt.columns else None,
            )
            st.plotly_chart(fig_fb, use_container_width=True)
        return

    sim = evolution[evolution["team"].isin(selected_teams)].copy()

    if use_rank:
        rank_rows = []
        for gp, grp in sim.groupby("games_played"):
            ordered = grp.sort_values(sim_metric_mean, ascending=False)
            for rank_i, (_, row) in enumerate(ordered.iterrows(), start=1):
                rank_rows.append({
                    "team": row["team"],
                    "games_played": gp,
                    "rank": rank_i,
                })
        rank_df = pd.DataFrame(rank_rows)
        fig_sim = _make_trajectory_figure(
            rank_df, selected_teams, color_map,
            y_col="rank", y_label="Standings rank (from mean)",
            title=f"Simulated standings rank ({target_season})",
            reverse_y=True,
        )
    else:
        fig_sim = _make_trajectory_figure(
            sim, selected_teams, color_map,
            y_col=sim_metric_mean, y_label=metric_label,
            title=f"Simulated {metric_label.lower()} ({target_season})",
            band_low=sim_metric_lo if sim_metric_lo in sim.columns else None,
            band_high=sim_metric_hi if sim_metric_hi in sim.columns else None,
        )

    st.plotly_chart(fig_sim, use_container_width=True)
    st.caption(
        "Shaded bands show the 5th–95th percentile across simulations. "
        "Observed path is actual results from the prior season; "
        "simulated path is the Monte Carlo target season."
    )
