"""
Reusable logo rendering helpers for MultiSport Elo Lab.

Performance notes
-----------------
Streamlit re-runs the entire script on every interaction, including every tab.
Never base64-encode a full league of logos on each run. This module:
  - resolves paths cheaply
  - uses st.image (Streamlit-managed, fast)
  - caches path lookups
  - only renders logos for the teams currently on screen
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import streamlit as st

try:
    from metadata import (
        get_logo_path,
        get_team_metadata,
        load_teams,
        list_teams,
        resolve_team_abbr,
    )
except ImportError:
    from app.metadata import (  # type: ignore
        get_logo_path,
        get_team_metadata,
        load_teams,
        list_teams,
        resolve_team_abbr,
    )


@st.cache_data(show_spinner=False)
def _cached_logo_path(sport: str, team_key: str) -> Optional[str]:
    """Return logo path as string (cacheable) or None."""
    path = get_logo_path(sport, team_key)
    return str(path) if path is not None else None


def render_logo(
    sport: str,
    abbr: str,
    width: int = 40,
    fallback_text: bool = False,
) -> None:
    """
    Render a single team logo via st.image (fast, cached path lookup).

    Accepts abbreviation or full team name.
    """
    path_str = _cached_logo_path(sport, abbr)
    if path_str is not None:
        st.image(path_str, width=width)
    elif fallback_text:
        label = resolve_team_abbr(sport, abbr)
        st.markdown(
            f"<div style='width:{width}px;height:{width}px;"
            f"display:flex;align-items:center;justify-content:center;"
            f"font-size:0.7rem;font-weight:600;color:#888;'>{label}</div>",
            unsafe_allow_html=True,
        )


def team_display_name(sport: str, abbr: str) -> str:
    """Prefer full team name; fall back to abbreviation."""
    meta = get_team_metadata(sport, abbr)
    return meta.get("name") or abbr


def render_ranked_elo_list(
    sport: str,
    latest_elo,
    *,
    max_rows: Optional[int] = None,
    logo_width: int = 36,
) -> None:
    """
    Ranked Elo table with logos.

    - Rank is a plain number (no medals)
    - Elo value uses neutral text color (not team primary color)
    """
    if latest_elo is None or latest_elo.empty:
        st.info("No Elo data to display.")
        return

    df = latest_elo.copy()
    if max_rows is not None:
        df = df.head(max_rows)

    h1, h2, h3, h4 = st.columns([0.6, 1.0, 4.6, 2.0])
    h1.markdown("**#**")
    h2.markdown("")
    h3.markdown("**Team**")
    h4.markdown("**Elo**")

    st.markdown(
        "<hr style='margin:0.3rem 0 0.5rem 0; border:none; border-top:1px solid #333;'>",
        unsafe_allow_html=True,
    )

    for rank, row in enumerate(df.itertuples(index=False), start=1):
        team = getattr(row, "team")
        elo = float(getattr(row, "elo"))

        c1, c2, c3, c4 = st.columns([0.6, 1.0, 4.6, 2.0])

        c1.markdown(
            f"<div style='padding-top:6px;font-weight:600;'>{rank}</div>",
            unsafe_allow_html=True,
        )

        with c2:
            render_logo(sport, team, width=logo_width, fallback_text=True)

        meta = get_team_metadata(sport, team)
        full_name = meta.get("name", team)
        conf = meta.get("conference", "")
        div = meta.get("division", "")
        sub = f"{conf} · {div}" if conf and div else conf or div or ""

        c3.markdown(
            f"<div style='padding-top:2px;'>"
            f"<strong>{full_name}</strong><br>"
            f"<span style='font-size:0.78rem;color:#999;'>{sub}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Neutral Elo color — no team primary color
        c4.markdown(
            f"<div style='padding-top:6px;font-size:1.1rem;font-weight:700;'>"
            f"{elo:.0f}</div>",
            unsafe_allow_html=True,
        )


def render_logo_strip(
    sport: str,
    teams: List[str],
    *,
    width: int = 32,
    max_show: int = 12,
) -> None:
    """Horizontal strip of logos for a small set of teams (e.g. selected / top N)."""
    if not teams:
        return

    show = list(teams)[:max_show]
    cols = st.columns(len(show))
    for col, abbr in zip(cols, show):
        with col:
            render_logo(sport, abbr, width=width, fallback_text=True)
            st.caption(resolve_team_abbr(sport, abbr))
