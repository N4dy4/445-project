"""Salamander ID & match finder: Streamlit frontend.

Run from the repo root:  streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from matcher import Matcher, load_history  # noqa: E402
from styles import build_css  # noqa: E402

HEADER_IMAGE_CANDIDATES = [
    APP_DIR / "assets" / "image_022006.jpg",
    APP_DIR / "image_022006.jpg",
    REPO_ROOT / "assets" / "image_022006.jpg",
    REPO_ROOT / "image_022006.jpg",
]


def resolve_header_image() -> Path | None:
    for candidate in HEADER_IMAGE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


st.set_page_config(
    page_title="Salamander ID System",
    page_icon=":material/database_search:",
    layout="wide",
)
st.markdown(build_css(resolve_header_image()), unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_matcher() -> Matcher:
    return Matcher(load_history())


matcher = get_matcher()
history_df = matcher.history
ranges = matcher.ranges

# --- Hero Header ---
with st.container(key="hero"):
    st.markdown('<div class="hero-badge">Mark-Recapture Field Console</div>', unsafe_allow_html=True)
    st.markdown("# Salamander ID System")
    st.markdown(
        "Log a new field capture to identify closely matched individuals on record, "
        "compare candidate morphometrics, and inspect prior sighting histories."
    )

# --- Dataset Overview Strip ---
unique_ids = int(history_df["Salamander ID"].nunique())
total_captures = len(history_df)
site_count = len(matcher.sites)
date_series = pd.to_datetime(history_df["t"], errors="coerce")
date_min = date_series.min()
date_max = date_series.max()

if pd.notna(date_min) and pd.notna(date_max):
    span_label = (
        f"{date_min:%Y}"
        if date_min.year == date_max.year
        else f"{date_min:%Y}\u2013{date_max:%Y}"
    )
else:
    span_label = "N/A"

k1, k2, k3, k4 = st.columns(4)
k1.metric("Unique IDs", f"{unique_ids:,}")
k2.metric("Total Captures", f"{total_captures:,}")
k3.metric("Survey Sites", f"{site_count}")
k4.metric("Record Span", span_label)

# --- Capture Input Section ---
st.markdown("### :material/note_alt: Capture details")

with st.form("capture_form"):
    c1, c2, c6 = st.columns([2, 1.5, 1.5])
    site = c1.selectbox(
        ":material/location_on: Site",
        matcher.sites,
        index=None,
        placeholder="Choose a survey site",
    )
    sex = c2.selectbox(
        ":material/wc: Sex",
        ["M", "F"],
        index=None,
        placeholder="Choose sex",
        format_func=lambda s: {"M": "Male", "F": "Female"}.get(str(s), str(s)),
    )
    top_k = c6.selectbox(
        ":material/database_search: Candidates shown",
        [3, 5],
        index=0,
        format_func=lambda n: f"Top {n} matches",
    )

    c3, c4, c5 = st.columns(3)
    weight_raw = c3.number_input(
        ":material/monitor_weight: Weight",
        value=None,
        min_value=0.0,
        step=0.1,
        format="%.1f",
        placeholder="e.g. 18.3",
        help=f"Record range: {ranges['Weight'][0]:.1f} – {ranges['Weight'][1]:.1f}",
    )
    tail_raw = c4.number_input(
        ":material/straighten: Tail Length",
        value=None,
        min_value=0.0,
        step=0.1,
        format="%.2f",
        placeholder="e.g. 10.4",
        help=f"Record range: {ranges['Tail Length'][0]:.1f} – {ranges['Tail Length'][1]:.1f}",
    )
    total_raw = c5.number_input(
        ":material/straighten: Total Length",
        value=None,
        min_value=0.0,
        step=0.1,
        format="%.2f",
        placeholder="e.g. 18.2",
        help=f"Record range: {ranges['Total Length'][0]:.1f} – {ranges['Total Length'][1]:.1f}",
    )

    st.caption("Use the same measurement units as the dataset's records.")
    submitted = st.form_submit_button(":material/search: Find closest matches")

# --- Results & Inspection Section ---
st.markdown("### :material/database_search: Closest matches")

if not submitted:
    st.markdown(
        '<div class="empty">Fill in the form above and press <b>Find closest matches</b> '
        "to rank candidate salamanders and inspect their sighting history.</div>",
        unsafe_allow_html=True,
    )
else:
    missing = [
        label
        for label, val in [
            ("Site", site),
            ("Sex", sex),
            ("Weight", weight_raw),
            ("Tail Length", tail_raw),
            ("Total Length", total_raw),
        ]
        if val is None or val == ""
    ]

    if missing:
        st.warning("Please fill in: " + ", ".join(missing))
    else:
        assert site is not None
        assert sex is not None
        assert weight_raw is not None
        assert tail_raw is not None
        assert total_raw is not None

        w_val = float(weight_raw)
        tail_val = float(tail_raw)
        total_val = float(total_raw)
        k_val = int(top_k) if top_k is not None else 3

        if total_val < tail_val:
            st.warning("Total Length can't be smaller than Tail Length. Please double-check.")
        else:
            query = {
                "Site": site,
                "Sex": sex,
                "Weight": w_val,
                "Tail Length": tail_val,
                "Total Length": total_val,
            }
            matches = matcher.find_matches(query, k=k_val)

            results_tab, compare_tab, log_tab = st.tabs(
                [
                    ":material/database_search: Ranked Candidates",
                    ":material/straighten: Morphometric Comparison",
                    ":material/calendar_month: Sighting History",
                ]
            )

            with results_tab:
                for i, row in matches.iterrows():
                    rank_num = int(str(i)) + 1 if isinstance(i, (int, float)) else 1
                    sex_label = "Male" if row["Sex"] == "M" else "Female"
                    seen_dt = pd.to_datetime(row["t"], errors="coerce")
                    seen_str = seen_dt.strftime("%b %d, %Y") if pd.notna(seen_dt) else "Unknown date"
                    sim_val = float(row["Similarity"])

                    with st.container(key=f"match-{i}"):
                        rank_col, detail_col, score_col = st.columns([0.7, 6.3, 1.4])
                        rank_col.markdown(
                            f'<div class="rank">{rank_num}</div>',
                            unsafe_allow_html=True,
                        )

                        if i == 0:
                            detail_col.markdown(
                                f"**{row['Salamander ID']}** "
                                '<span class="top-tag">Best Match</span>',
                                unsafe_allow_html=True,
                            )
                        else:
                            detail_col.markdown(f"**{row['Salamander ID']}**")

                        detail_col.markdown(
                            f":material/location_on: **{row['Site']}** &nbsp;&bull;&nbsp; "
                            f":material/wc: {sex_label} &nbsp;&bull;&nbsp; "
                            f":material/monitor_weight: {float(row['Weight']):.1f} &nbsp;&bull;&nbsp; "
                            f":material/straighten: Tail {float(row['Tail Length']):.2f} &nbsp;&bull;&nbsp; "
                            f":material/straighten: Total {float(row['Total Length']):.2f} &nbsp;&bull;&nbsp; "
                            f":material/calendar_month: {seen_str}"
                        )
                        detail_col.progress(max(0.0, min(1.0, sim_val / 100.0)))

                        score_col.markdown(
                            f'<div class="score-box">'
                            f'<div class="score-val">{sim_val:.0f}%</div>'
                            f'<div class="score-lbl">similarity</div>'
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                st.caption("Similarity is a relative closeness score, not a probability of identity.")

            with compare_tab:
                comp_rows = []
                for _, row in matches.iterrows():
                    rec_w = float(row["Weight"])
                    rec_tail = float(row["Tail Length"])
                    rec_total = float(row["Total Length"])
                    comp_rows.append(
                        {
                            "Salamander ID": row["Salamander ID"],
                            "Similarity (%)": float(row["Similarity"]),
                            "Site Match": "Yes" if row["Site"] == site else "No",
                            "Sex Match": "Yes" if row["Sex"] == sex else "No",
                            "Weight (Rec / Δ)": f"{rec_w:.1f} ({rec_w - w_val:+.1f})",
                            "Tail (Rec / Δ)": f"{rec_tail:.2f} ({rec_tail - tail_val:+.2f})",
                            "Total (Rec / Δ)": f"{rec_total:.2f} ({rec_total - total_val:+.2f})",
                        }
                    )
                st.dataframe(pd.DataFrame(comp_rows), width="stretch", hide_index=True)

            with log_tab:
                candidate_ids = matches["Salamander ID"].tolist()
                selected_id = st.selectbox(
                    "Inspect full capture history for candidate ID:",
                    candidate_ids,
                    key="history-candidate-select",
                )
                animal_history = history_df[history_df["Salamander ID"] == selected_id].copy()
                animal_history["_dt"] = pd.to_datetime(animal_history["t"], errors="coerce")
                animal_history = animal_history.sort_values("_dt", ascending=False)
                animal_history["Date"] = animal_history["_dt"].dt.strftime("%Y-%m-%d").fillna("Unknown")

                display_cols = [
                    c
                    for c in ["Date", "Site", "Sex", "Weight", "SVL", "Tail Length", "Total Length"]
                    if c in animal_history.columns
                ]
                st.dataframe(animal_history[display_cols], width="stretch", hide_index=True)

st.markdown(
    '<div class="footer">CMPSC 445 Project &#10035; Salamander ID System &#10035; Made with Streamlit</div>',
    unsafe_allow_html=True,
)