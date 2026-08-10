"""
Playoff visualizations for MultiSport Elo Lab.

Playoff Odds table: style inspired by MoneyPuck (https://moneypuck.com/predictions.htm).
All underlying probabilities are produced by this project's Elo + Monte Carlo engine.

Round-path color palette (documentation numbers only):
  Color 1 — championship / win cup          #6F263D
  Color 2 — reach championship / make final #236192
  Color 3 — make 3rd round / conf. finals   #006847
  Color 4 — make 2nd round                  #F47A38
  Color 5 — make playoffs                   #00205B
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

try:
    from components.logos import _cached_logo_path, team_display_name
except ImportError:
    from app.components.logos import _cached_logo_path, team_display_name  # type: ignore

try:
    from metadata import load_teams, resolve_team_abbr
except ImportError:
    from app.metadata import load_teams, resolve_team_abbr  # type: ignore


# ---------------------------------------------------------------------------
# Round-path palette (Color 1 … Color 5) — see module docstring
# ---------------------------------------------------------------------------
PATH_COLORS = {
    1: "#6F263D",  # championship
    2: "#236192",  # reach final
    3: "#006847",  # make 3rd round
    4: "#F47A38",  # make 2nd round
    5: "#00205B",  # make playoffs
}

# Map friendly round labels → palette index (outer → inner uses 5…1)
PATH_COLOR_BY_LABEL = {
    # NHL
    "Make Playoffs": 5,
    "Make 2nd Round": 4,
    "Make 3rd Round": 3,
    "Make Final": 2,
    "Win Cup": 1,
    # NFL
    "Make Divisional": 4,
    "Make Conference": 3,
    "Make Super Bowl": 2,
    "Win Super Bowl": 1,
    # NBA
    "Make Play-In": 5,
    "Make Conf. Finals": 3,
    "Make Finals": 2,
    "Win Title": 1,
}


# ---------------------------------------------------------------------------
# Sport-specific column layout (MoneyPuck-style names)
# ---------------------------------------------------------------------------
PLAYOFF_TABLE_SPEC = {
    "NFL": {
        "round_keys": ["Wild Card", "Divisional", "Conference", "Super Bowl", "Champion"],
        "round_labels": {
            "Wild Card": "Make Playoffs",
            "Divisional": "Make Divisional",
            "Conference": "Make Conference",
            "Super Bowl": "Make Super Bowl",
            "Champion": "Win Super Bowl",
        },
        # Rings ordered innermost → outermost for the circular graphic
        "ring_keys_inner_to_outer": [
            "Champion",
            "Super Bowl",
            "Conference",
            "Divisional",
            "Wild Card",
        ],
        "sort_default": "Make Playoffs",
        "champ_label": "Win Super Bowl",
        "metric_label": "Wins",
        "conferences": ("AFC", "NFC"),
    },
    "NHL": {
        "round_keys": [
            "First Round",
            "Second Round",
            "Conference Finals",
            "Stanley Cup Final",
            "Champion",
        ],
        "round_labels": {
            "First Round": "Make Playoffs",
            "Second Round": "Make 2nd Round",
            "Conference Finals": "Make 3rd Round",
            "Stanley Cup Final": "Make Final",
            "Champion": "Win Cup",
        },
        "ring_keys_inner_to_outer": [
            "Champion",
            "Stanley Cup Final",
            "Conference Finals",
            "Second Round",
            "First Round",
        ],
        "sort_default": "Make Playoffs",
        "champ_label": "Win Cup",
        "metric_label": "Points",
        "conferences": ("Eastern", "Western"),
    },
    "NBA": {
        "round_keys": [
            "Play-In",
            "First Round",
            "Conference Semifinals",
            "Conference Finals",
            "NBA Finals",
            "Champion",
        ],
        "round_labels": {
            "Play-In": "Make Play-In",
            "First Round": "Make Playoffs",
            "Conference Semifinals": "Make 2nd Round",
            "Conference Finals": "Make Conf. Finals",
            "NBA Finals": "Make Finals",
            "Champion": "Win Title",
        },
        "ring_keys_inner_to_outer": [
            "Champion",
            "NBA Finals",
            "Conference Finals",
            "Conference Semifinals",
            "First Round",
            "Play-In",
        ],
        "sort_default": "Make Playoffs",
        "champ_label": "Win Title",
        "metric_label": "Wins",
        "conferences": ("Eastern", "Western"),
    },
}


def _prob_to_pct(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    if v <= 1.5:
        v *= 100.0
    return round(v, 1)


def _blue_shade(pct: float) -> str:
    p = max(0.0, min(100.0, float(pct))) / 100.0
    r = int(255 - p * (255 - 30))
    g = int(255 - p * (255 - 136))
    b = int(255 - p * (255 - 229))
    return f"rgb({r},{g},{b})"


def _text_color_for_bg(pct: float) -> str:
    return "#0f172a" if pct < 55 else "#ffffff"


@st.cache_data(show_spinner=False)
def _logo_data_uri(sport: str, abbr: str) -> Optional[str]:
    path_str = _cached_logo_path(sport, abbr)
    if not path_str:
        return None
    path = Path(path_str)
    if not path.is_file():
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _teams_by_conference(sport: str) -> Dict[str, List[str]]:
    sport_u = sport.upper()
    try:
        meta = load_teams(sport_u)
    except Exception:
        return {}
    out: Dict[str, List[str]] = {}
    for abbr, info in meta.items():
        conf = info.get("conference") or "Other"
        out.setdefault(conf, []).append(abbr)
    for conf in out:
        out[conf] = sorted(out[conf])
    return out


def _team_primary_color(sport: str, abbr: str) -> str:
    try:
        meta = load_teams(sport.upper())
    except Exception:
        return "#64748b"
    info = meta.get(abbr) or {}
    return info.get("primary_color") or "#64748b"


# ---------------------------------------------------------------------------
# Playoff odds table
# ---------------------------------------------------------------------------
def build_playoff_odds_frame(
    sport: str,
    playoff_probs: Dict[str, Dict[str, float]],
    achievement_probs: Optional[pd.DataFrame] = None,
    summary: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    sport_u = sport.upper()
    spec = PLAYOFF_TABLE_SPEC.get(sport_u)
    if not spec or not playoff_probs:
        return pd.DataFrame()

    rows = []
    for team, probs in playoff_probs.items():
        row = {"team": resolve_team_abbr(sport_u, team) or team}
        for key in spec["round_keys"]:
            label = spec["round_labels"].get(key, key)
            row[label] = _prob_to_pct(probs.get(key, 0.0))
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    if achievement_probs is not None and not achievement_probs.empty:
        ach = achievement_probs.copy()
        if "team" in ach.columns:
            ach["team"] = ach["team"].map(lambda t: resolve_team_abbr(sport_u, t) or t)
            rename = {
                "make_playoffs": "Make Playoffs (RS)",
                "first_in_division": "1st in Division",
                "first_in_conference": "1st in Conference",
                "first_in_league": "1st in League",
                "home_ice": "Home Ice / Court",
            }
            keep = ["team"] + [c for c in rename if c in ach.columns]
            ach = ach[keep].rename(columns=rename)
            for c in ach.columns:
                if c != "team":
                    ach[c] = ach[c].map(_prob_to_pct)
            df = df.merge(ach, on="team", how="left")

    if summary is not None and not summary.empty and "team" in summary.columns:
        sm = summary.copy()
        sm["team"] = sm["team"].map(lambda t: resolve_team_abbr(sport_u, t) or t)
        metric_col = None
        if sport_u == "NHL":
            for c in ("mean_points", "median_points", "points"):
                if c in sm.columns:
                    metric_col = c
                    break
        else:
            for c in ("median_wins", "mean_wins", "wins"):
                if c in sm.columns:
                    metric_col = c
                    break
        if metric_col:
            label = spec["metric_label"]
            sm = sm[["team", metric_col]].rename(columns={metric_col: label})
            sm[label] = sm[label].map(lambda x: round(float(x), 1))
            df = df.merge(sm, on="team", how="left")

    sort_col = spec["sort_default"]
    if sort_col in df.columns:
        df = df.sort_values(sort_col, ascending=False)
    elif spec["champ_label"] in df.columns:
        df = df.sort_values(spec["champ_label"], ascending=False)

    return df.reset_index(drop=True)


def render_playoff_odds_table(
    sport: str,
    playoff_probs: Dict[str, Dict[str, float]],
    achievement_probs: Optional[pd.DataFrame] = None,
    summary: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    df = build_playoff_odds_frame(sport, playoff_probs, achievement_probs, summary)
    if df.empty:
        st.caption("Playoff probability data not available for this run.")
        return df

    sport_u = sport.upper()
    spec = PLAYOFF_TABLE_SPEC[sport_u]
    metric_col = spec["metric_label"] if spec["metric_label"] in df.columns else None

    preferred = (
        ["team"]
        + [
            spec["round_labels"][k]
            for k in spec["round_keys"]
            if spec["round_labels"][k] in df.columns
        ]
        + ([metric_col] if metric_col else [])
        + [
            c
            for c in (
                "1st in Division",
                "1st in Conference",
                "1st in League",
                "Home Ice / Court",
                "Make Playoffs (RS)",
            )
            if c in df.columns
        ]
    )
    seen = set()
    ordered = []
    for c in preferred:
        if c in df.columns and c not in seen:
            ordered.append(c)
            seen.add(c)
    for c in df.columns:
        if c not in seen:
            ordered.append(c)
            seen.add(c)
    df = df[ordered]

    # Sort controls on the main table (no duplicate expander table)
    sort_candidates = [c for c in df.columns if c != "team"]
    default_sort = spec["sort_default"] if spec["sort_default"] in sort_candidates else (
        spec["champ_label"] if spec["champ_label"] in sort_candidates else sort_candidates[0]
    )
    c1, c2 = st.columns([3, 1])
    with c1:
        sort_by = st.selectbox(
            "Sort table by",
            options=sort_candidates,
            index=sort_candidates.index(default_sort) if default_sort in sort_candidates else 0,
            key=f"playoff_table_sort_{sport_u}",
        )
    with c2:
        ascending = st.toggle("Ascending", value=False, key=f"playoff_table_asc_{sport_u}")
    df = df.sort_values(sort_by, ascending=ascending).reset_index(drop=True)

    header_cells = []
    for c in df.columns:
        label = "Team" if c == "team" else c
        header_cells.append(
            f"<th style='text-align:{'left' if c == 'team' else 'center'};"
            f"padding:6px 8px;font-size:0.78rem;white-space:nowrap;'>{label}</th>"
        )
    thead = "<tr>" + "".join(header_cells) + "</tr>"

    body_rows = []
    for _, row in df.iterrows():
        abbr = str(row["team"])
        uri = _logo_data_uri(sport_u, abbr)
        if uri:
            team_cell = (
                f"<td style='padding:4px 8px;white-space:nowrap;'>"
                f"<img src='{uri}' width='22' height='22' "
                f"style='vertical-align:middle;margin-right:6px;'/>"
                f"<span style='font-weight:600;font-size:0.85rem;'>{abbr}</span></td>"
            )
        else:
            team_cell = (
                f"<td style='padding:4px 8px;font-weight:600;font-size:0.85rem;'>{abbr}</td>"
            )
        cells = [team_cell]
        for c in df.columns:
            if c == "team":
                continue
            val = row[c]
            if pd.isna(val):
                cells.append(
                    "<td style='text-align:center;padding:4px 6px;color:#94a3b8;'>—</td>"
                )
                continue
            if metric_col and c == metric_col:
                cells.append(
                    f"<td style='text-align:center;padding:4px 6px;"
                    f"font-variant-numeric:tabular-nums;'>{float(val):.1f}</td>"
                )
            else:
                pct = float(val)
                bg = _blue_shade(pct)
                fg = _text_color_for_bg(pct)
                cells.append(
                    f"<td style='text-align:center;padding:4px 6px;"
                    f"background:{bg};color:{fg};"
                    f"font-variant-numeric:tabular-nums;font-size:0.85rem;'>"
                    f"{pct:.1f}%</td>"
                )
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    html = (
        "<div style='overflow-x:auto;border:1px solid #e2e8f0;border-radius:8px;'>"
        "<table style='border-collapse:collapse;width:100%;'>"
        f"<thead style='background:#f8fafc;border-bottom:2px solid #cbd5e1;'>{thead}</thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table></div>"
    )
    st.markdown(html, unsafe_allow_html=True)
    st.caption(
        "Visualization style inspired by [MoneyPuck](https://moneypuck.com/predictions.htm). "
        "Probabilities from this project's Elo + Monte Carlo engine."
    )
    return df


# ---------------------------------------------------------------------------
# Playoff spirals — one per conference
# ---------------------------------------------------------------------------
def _conference_probs(
    sport: str,
    playoff_probs: Dict[str, Dict[str, float]],
    conference: str,
) -> Dict[str, Dict[str, float]]:
    """Filter playoff_probs to teams in the given conference; keys are abbreviations."""
    sport_u = sport.upper()
    by_conf = _teams_by_conference(sport_u)
    members = set(by_conf.get(conference, []))
    out: Dict[str, Dict[str, float]] = {}
    for team, probs in playoff_probs.items():
        abbr = resolve_team_abbr(sport_u, team) or team
        if abbr in members:
            out[abbr] = probs
    for abbr in members:
        out.setdefault(abbr, {})
    return out


def _build_playoff_spiral(
    sport: str,
    conference: str,
    conf_probs: Dict[str, Dict[str, float]],
    round_labels: Dict[str, str],
    radius_key: str,
    radius_label: str,
) -> go.Figure:
    """
    Playoff spiral for one conference.

    Each team is a wedge; radius encodes the selected round probability
    (scaled so the conference leader reaches 100% of the chart radius).
    Wedge color = team primary. Hover shows the full playoff path.
    """
    sport_u = sport.upper()

    ranked = sorted(
        conf_probs.keys(),
        key=lambda t: (-float(conf_probs[t].get(radius_key, 0.0)), t),
    )
    if not ranked:
        return go.Figure()

    labels, radii, colors, hover = [], [], [], []
    for t in ranked:
        probs = conf_probs[t]
        p_r = _prob_to_pct(probs.get(radius_key, 0.0))
        labels.append(t)
        radii.append(p_r)
        colors.append(_team_primary_color(sport_u, t))
        path_bits = []
        for key, lab in round_labels.items():
            path_bits.append(f"{lab}: {_prob_to_pct(probs.get(key, 0.0)):.1f}%")
        name = team_display_name(sport_u, t)
        hover.append(
            f"<b>{name}</b> ({t})<br><b>{radius_label}: {p_r:.1f}%</b><br>"
            + "<br>".join(path_bits)
        )

    # Scale so the top value uses the full radius (100% of the polar domain)
    r_max = max(radii) if radii else 1.0
    if r_max <= 0:
        r_max = 1.0
    r_plot = [r / r_max * 100.0 for r in radii]  # top team → 100 on the spiral axis

    fig = go.Figure(
        go.Barpolar(
            r=r_plot,
            theta=labels,
            marker_color=colors,
            marker_line_color="rgba(15,23,42,0.35)",
            marker_line_width=1,
            opacity=0.92,
            hovertext=hover,
            hoverinfo="text",
            customdata=radii,  # actual % for any future use
        )
    )

    import math

    n = len(labels)
    images = []
    annotations = []
    cx, cy, scale = 0.5, 0.50, 0.34
    for i, (abbr, r_val) in enumerate(zip(labels, r_plot)):
        theta_deg = i * (360.0 / n)
        r_norm = 0.85 * (r_val / 100.0)
        rad = math.radians(theta_deg)
        x = r_norm * math.sin(rad)
        y = r_norm * math.cos(rad)
        px = cx + scale * x
        py = cy + scale * y
        uri = _logo_data_uri(sport_u, abbr)
        if uri:
            images.append(
                dict(
                    source=uri,
                    xref="paper",
                    yref="paper",
                    x=px,
                    y=py,
                    sizex=0.042,
                    sizey=0.042,
                    xanchor="center",
                    yanchor="middle",
                    layer="above",
                )
            )
        else:
            annotations.append(
                dict(
                    x=px,
                    y=py,
                    xref="paper",
                    yref="paper",
                    text=f"<b>{abbr}</b>",
                    showarrow=False,
                    font=dict(size=9, color="#0f172a"),
                )
            )

    fig.update_layout(
        title=dict(
            text=f"{conference} — {radius_label}",
            x=0.5,
            xanchor="center",
            font=dict(size=14),
        ),
        polar=dict(
            domain=dict(x=[0.06, 0.94], y=[0.06, 0.94]),
            radialaxis=dict(
                range=[0, 100],
                ticksuffix="%",
                angle=90,
                tickvals=[0, 25, 50, 75, 100],
                # Tick labels show relative scale (leader = 100%); hover has true %
                ticktext=["0", "", "", "", "max"],
                gridcolor="rgba(148,163,184,0.35)",
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                gridcolor="rgba(148,163,184,0.25)",
            ),
            bgcolor="rgba(248,250,252,1)",
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=48, b=20),
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        images=images,
        annotations=annotations,
    )
    return fig


def render_playoff_spirals(
    sport: str,
    playoff_probs: Dict[str, Dict[str, float]],
) -> None:
    """
    Two playoff spirals — one per conference.
    Dropdown selects which round probability sets the radius (leader fills the circle).
    Hover always shows the full playoff path for that team.
    """
    sport_u = sport.upper()
    spec = PLAYOFF_TABLE_SPEC.get(sport_u)
    if not spec or not playoff_probs:
        return

    conferences = spec.get("conferences") or tuple(_teams_by_conference(sport_u).keys())
    ordered_labels = {k: spec["round_labels"][k] for k in spec["round_keys"]}
    # Dropdown options: label → engine key
    options = [(spec["round_labels"][k], k) for k in spec["round_keys"]]
    label_list = [lab for lab, _ in options]
    # Default to championship (last key is usually Champion)
    default_lab = spec["champ_label"]
    if default_lab not in label_list:
        default_lab = label_list[-1]

    radius_label = st.selectbox(
        "Radial metric (sets bar length)",
        options=label_list,
        index=label_list.index(default_lab),
        key=f"spiral_metric_{sport_u}",
        help="Bars are scaled so the conference leader on this metric fills the full radius. "
        "Hover any wedge for that team’s complete playoff path.",
    )
    radius_key = dict(options)[radius_label]

    cols = st.columns(len(conferences))
    for col, conf in zip(cols, conferences):
        with col:
            conf_probs = _conference_probs(sport_u, playoff_probs, conf)
            if not conf_probs:
                st.caption(f"No {conf} teams in results.")
                continue
            fig = _build_playoff_spiral(
                sport_u,
                conf,
                conf_probs,
                ordered_labels,
                radius_key=radius_key,
                radius_label=radius_label,
            )
            st.plotly_chart(fig, use_container_width=True)

    st.caption(
        f"Playoff spirals ({' · '.join(conferences)}): "
        f"radius encodes **{radius_label}** (conference leader = full radius); "
        "color = team primary; hover for the full playoff path."
    )


# ---------------------------------------------------------------------------
# Playoff path bars (Color 1…5 palette)
# ---------------------------------------------------------------------------
def render_playoff_path_bars(
    sport: str,
    playoff_probs: Dict[str, Dict[str, float]],
    top_n: int = 12,
) -> None:
    sport_u = sport.upper()
    spec = PLAYOFF_TABLE_SPEC.get(sport_u)
    if not spec or not playoff_probs:
        return

    ranked = sorted(
        playoff_probs.items(),
        key=lambda kv: float(kv[1].get("Champion", 0.0)),
        reverse=True,
    )[: max(1, top_n)]

    records = []
    for team, probs in ranked:
        abbr = resolve_team_abbr(sport_u, team) or team
        for key in spec["round_keys"]:
            lab = spec["round_labels"].get(key, key)
            records.append(
                {
                    "team": abbr,
                    "round": lab,
                    "prob": _prob_to_pct(probs.get(key, 0.0)),
                }
            )
    path_df = pd.DataFrame(records)
    if path_df.empty:
        return

    order = [resolve_team_abbr(sport_u, t) or t for t, _ in ranked]
    round_order = [
        spec["round_labels"][k]
        for k in spec["round_keys"]
        if spec["round_labels"][k] in set(path_df["round"])
    ]
    color_map = {
        lab: PATH_COLORS[PATH_COLOR_BY_LABEL[lab]]
        for lab in round_order
        if lab in PATH_COLOR_BY_LABEL
    }

    fig = px.bar(
        path_df,
        x="prob",
        y="team",
        color="round",
        orientation="h",
        category_orders={"team": order, "round": round_order},
        color_discrete_map=color_map,
        labels={"prob": "Probability (%)", "team": "", "round": "Round"},
        title=f"Playoff path probabilities (top {len(order)})",
        barmode="group",
    )
    fig.update_layout(
        height=max(360, 36 * len(order) + 80),
        legend_title_text="",
        margin=dict(l=10, r=10, t=50, b=30),
        xaxis=dict(ticksuffix="%", range=[0, 105]),
    )
    st.plotly_chart(fig, use_container_width=True)
