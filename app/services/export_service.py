"""
Export service for MultiSport Elo Lab.

Builds a single multi-sheet Excel workbook containing all currently available
results (config, simulation summary, achievement/playoff probabilities,
Elo ratings, and evaluation metrics) so the user can download everything
in one click.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd


def _safe_df(obj: Any) -> Optional[pd.DataFrame]:
    """Return a DataFrame if possible, otherwise None."""
    if obj is None:
        return None
    if isinstance(obj, pd.DataFrame):
        return obj.copy()
    if isinstance(obj, dict):
        try:
            # Common pattern: {team: {metric: value, ...}, ...}
            sample = next(iter(obj.values()), None)
            if isinstance(sample, dict):
                return (
                    pd.DataFrame.from_dict(obj, orient="index")
                    .reset_index()
                    .rename(columns={"index": "team"})
                )
            return pd.DataFrame(obj)
        except Exception:
            return None
    return None


def _config_to_df(config: dict, meta: dict) -> pd.DataFrame:
    """Flatten model config + run metadata into a two-column DataFrame."""
    rows = []

    # Run metadata first
    for k, v in meta.items():
        rows.append({"key": k, "value": v})

    rows.append({"key": "---", "value": "---"})

    # Top-level config
    for k, v in config.items():
        if k == "adjustments":
            continue
        rows.append({"key": k, "value": v})

    # Adjustments (nested)
    adjustments = config.get("adjustments", {}) or {}
    for name, params in adjustments.items():
        if isinstance(params, dict):
            for pk, pv in params.items():
                rows.append({"key": f"adjustments.{name}.{pk}", "value": pv})
        else:
            rows.append({"key": f"adjustments.{name}", "value": params})

    return pd.DataFrame(rows)


def build_full_export(session_state) -> bytes:
    """
    Build a multi-sheet Excel workbook from the current session state.

    Sheets produced (only those with data):
      - Config
      - Simulation_Summary
      - Achievement_Playoff
      - Elo_Ratings
      - Evaluation

    Returns
    -------
    bytes
        Excel file content ready for st.download_button.
    """
    sport = session_state.get("sport", "UNKNOWN")
    season = session_state.get("season", "UNKNOWN")
    is_default = session_state.get("is_default_run", False)
    final_config = (
        session_state.get("final_config")
        or session_state.get("last_config")
        or {}
    )
    sim_results = session_state.get("simulation_results")

    # ----- Metadata for Config sheet -----
    meta = {
        "export_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "sport": sport,
        "season": season,
        "is_default_run": is_default,
        "rating_source": session_state.get("rating_source"),
        "rating_basis": session_state.get("rating_basis"),
        "apply_regression": session_state.get("apply_regression"),
    }

    # Try to pull n_sims if present
    if isinstance(sim_results, dict):
        raw = sim_results.get("raw")
        if isinstance(raw, pd.DataFrame) and "sim_id" in raw.columns:
            meta["n_sims"] = int(raw["sim_id"].nunique())
        elif "n_sims" in sim_results:
            meta["n_sims"] = sim_results["n_sims"]

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # 1. Config
        config_df = _config_to_df(final_config, meta)
        config_df.to_excel(writer, sheet_name="Config", index=False)

        # 2. Simulation Summary
        summary_df = None
        if isinstance(sim_results, dict):
            summary_df = _safe_df(sim_results.get("summary"))
        if summary_df is not None and not summary_df.empty:
            summary_df.to_excel(writer, sheet_name="Simulation_Summary", index=False)

        # 3. Achievement + Playoff probabilities
        ach_df = None
        playoff_df = None
        if isinstance(sim_results, dict):
            ach_df = _safe_df(sim_results.get("achievement_probs"))
            raw_playoff = (
                sim_results.get("playoff_probs")
                or sim_results.get("playoff_probabilities")
            )
            playoff_df = _safe_df(raw_playoff)

        if ach_df is not None and playoff_df is not None:
            # Prefer a single merged sheet when both exist
            merge_on = "team" if "team" in ach_df.columns and "team" in playoff_df.columns else None
            if merge_on:
                merged = ach_df.merge(
                    playoff_df, on=merge_on, how="outer", suffixes=("", "_playoff")
                )
                merged.to_excel(writer, sheet_name="Achievement_Playoff", index=False)
            else:
                ach_df.to_excel(writer, sheet_name="Achievement", index=False)
                playoff_df.to_excel(writer, sheet_name="Playoff", index=False)
        elif ach_df is not None and not ach_df.empty:
            ach_df.to_excel(writer, sheet_name="Achievement_Playoff", index=False)
        elif playoff_df is not None and not playoff_df.empty:
            playoff_df.to_excel(writer, sheet_name="Achievement_Playoff", index=False)

        # 4. Elo Ratings
        elo_df = None
        if isinstance(sim_results, dict):
            elo_df = (
                _safe_df(sim_results.get("final_elo"))
                or _safe_df(sim_results.get("elo_ratings"))
                or _safe_df(sim_results.get("team_elo"))
            )
        if elo_df is None:
            elo_df = _safe_df(session_state.get("elo_ratings"))
        if elo_df is not None and not elo_df.empty:
            elo_df.to_excel(writer, sheet_name="Elo_Ratings", index=False)

        # 5. Evaluation metrics (if present)
        eval_df = None
        eval_data = (
            session_state.get("evaluation_results")
            or session_state.get("model_metrics")
        )
        if eval_data is not None:
            eval_df = _safe_df(eval_data)
        if eval_df is not None and not eval_df.empty:
            eval_df.to_excel(writer, sheet_name="Evaluation", index=False)

    buffer.seek(0)
    return buffer.getvalue()


def make_export_filename(session_state) -> str:
    """Generate a clean, informative filename."""
    sport = str(session_state.get("sport", "sport")).lower()
    season = str(session_state.get("season", "season"))
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    return f"multisport_elo_{sport}_{season}_{ts}.xlsx"
