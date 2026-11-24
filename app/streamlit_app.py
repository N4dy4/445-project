"""Salamander match finder: Streamlit frontend.

Run from the repo root:  streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matcher import Matcher, NUMERIC, load_history  # noqa: E402
from styles import CSS  # noqa: E402

st.set_page_config(page_title="Salamander Match Finder", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def get_matcher() -> Matcher:
    return Matcher(load_history())


matcher = get_matcher()
ranges = matcher.ranges

with st.container(key="hero"):
    st.markdown("# :material/frame_bug: Salamander Match Finder")
    st.markdown(
        "Enter a new capture's measurements and we'll surface the three closest "
        "animals already on record."
    )

st.markdown("### :material/note_alt: Capture details")

with st.form("capture_form"):
    c1, c2 = st.columns(2)
    site = c1.selectbox(
        ":material/location_on: Site", matcher.sites, index=None,
        placeholder="Choose or type a site",
    )
    sex = c2.selectbox(
        ":material/wc: Sex", ["M", "F"], index=None, placeholder="Choose sex",
        format_func=lambda s: {"M": "Male", "F": "Female"}[s],
    )

    c3, c4, c5 = st.columns(3)
    weight = c3.number_input(
        ":material/monitor_weight: Weight", value=None, min_value=0.0, step=0.1, format="%.1f",
        placeholder="e.g. 18.3",
        help=f"Typical range in the records: {ranges['Weight'][0]:.1f} – {ranges['Weight'][1]:.1f}",
    )
    tail = c4.number_input(
        ":material/straighten: Tail Length", value=None, min_value=0.0, step=0.1, format="%.2f",
        placeholder="e.g. 10.4",
        help=f"Typical range in the records: {ranges['Tail Length'][0]:.1f} – {ranges['Tail Length'][1]:.1f}",
    )
    total = c5.number_input(
        ":material/straighten: Total Length", value=None, min_value=0.0, step=0.1, format="%.2f",
        placeholder="e.g. 18.2",
        help=f"Typical range in the records: {ranges['Total Length'][0]:.1f} – {ranges['Total Length'][1]:.1f}",
    )
    st.caption("Use the same units as the dataset's records.")
    submitted = st.form_submit_button(":material/search: Find closest matches")

st.markdown("### :material/database_search: Closest matches")

if not submitted:
    st.markdown(
        '<div class="empty">Fill in the form above and press <b>Find closest matches</b> '
        "to see results here.</div>",
        unsafe_allow_html=True,
    )
else:
    missing = [n for n, v in [("Site", site), ("Sex", sex), ("Weight", weight),
                              ("Tail Length", tail), ("Total Length", total)] if v in (None, "")]
    if missing:
        st.warning("Please fill in: " + ", ".join(missing))
    elif total < tail:
        st.warning("Total Length can't be smaller than Tail Length. Please double-check.")
    else:
        matches = matcher.find_matches(
            {"Site": site, "Sex": sex, "Weight": weight, "Tail Length": tail, "Total Length": total},
            k=3,
        )
        for i, row in matches.iterrows():
            sex_label = "Male" if row["Sex"] == "M" else "Female"
            with st.container(key=f"match-{i}"):
                rank, details, score = st.columns([0.6, 6, 1])
                rank.markdown(f'<div class="rank">{i + 1}</div>', unsafe_allow_html=True)
                details.markdown(f"**{row['Salamander ID']}**")
                details.markdown(
                    f":material/location_on: {row['Site']} | "
                    f":material/wc: {sex_label} | "
                    f":material/monitor_weight: Weight {row['Weight']:.1f} | "
                    f":material/straighten: Tail {row['Tail Length']:.2f} | "
                    f":material/straighten: Total {row['Total Length']:.2f} | "
                    f":material/calendar_month: Seen {row['t']:%b %d, %Y}"
                )
                details.progress(float(row["Similarity"]) / 100)
                score.markdown(f"**{row['Similarity']:.0f}%**  \nsimilarity")
        st.caption("Similarity is a relative closeness score, not a probability of identity.")

st.markdown('<div class="footer">CMPSC 445 Project | Made with Streamlit</div>', unsafe_allow_html=True)
