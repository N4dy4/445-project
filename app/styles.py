"""Responsive field-guide styling with a layered photo-gradient hero header."""

from __future__ import annotations

import base64
from pathlib import Path

FOREST_DARK = "#122417"
MOSS_PRIMARY = "#1E5631"
MOSS_SOFT = "#2E7D46"
MOSS_LIGHT = "#E9EEEA"
AMBER_ACCENT = "#D96B27"
AMBER_HOVER = "#B85519"
PARCHMENT = "#F6F4EE"
SURFACE = "#FFFFFF"
SURFACE_MUTED = "#ECE8DC"
INK = "#1D241E"
INK_MUTED = "#59635A"
BORDER = "#DDD6C5"


def _image_to_data_uri(image_path: Path | None) -> str:
    """Return a data URI for the header image if present, else empty string."""
    if image_path is None or not image_path.exists():
        return ""
    suffix = image_path.suffix.lower().lstrip(".")
    mime = "jpeg" if suffix in ("jpg", "jpeg") else (suffix or "jpeg")
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/{mime};base64,{encoded}"


def build_css(header_image_path: Path | None = None) -> str:
    """Generate responsive stylesheet for the Salamander ID Streamlit app."""
    data_uri = _image_to_data_uri(header_image_path)

    if data_uri:
        hero_bg = (
            "background: "
            "linear-gradient(120deg, rgba(14, 31, 19, 0.88) 0%, "
            "rgba(24, 62, 34, 0.74) 52%, rgba(15, 24, 18, 0.86) 100%), "
            f'url("{data_uri}") center 62% / cover no-repeat;'
        )
        photo_layer = f"""
        .st-key-hero::before {{
          content: "";
          position: absolute;
          inset: 0;
          background: url("{data_uri}") center 62% / cover no-repeat;
          opacity: 0.28;
          filter: saturate(1.1) contrast(1.05);
          pointer-events: none;
          z-index: 0;
        }}
        .st-key-hero > * {{
          position: relative;
          z-index: 1;
        }}
        """
    else:
        hero_bg = (
            f"background: linear-gradient(120deg, {FOREST_DARK} 0%, "
            f"{MOSS_PRIMARY} 60%, #172B1D 100%);"
        )
        photo_layer = ""

    return f"""
<style>
:root {{
  --forest-dark: {FOREST_DARK};
  --moss: {MOSS_PRIMARY};
  --moss-soft: {MOSS_SOFT};
  --moss-light: {MOSS_LIGHT};
  --amber: {AMBER_ACCENT};
  --amber-hover: {AMBER_HOVER};
  --parchment: {PARCHMENT};
  --surface: {SURFACE};
  --surface-muted: {SURFACE_MUTED};
  --ink: {INK};
  --ink-muted: {INK_MUTED};
  --border: {BORDER};
}}

/* Canvas & responsive container */
.stApp {{
  background:
    radial-gradient(circle at 90% 8%, rgba(46, 125, 70, 0.07), transparent 36%),
    var(--parchment);
  color: var(--ink);
  overflow-x: hidden;
}}

header[data-testid="stHeader"] {{
  background: transparent;
}}

.block-container {{
  max-width: 1040px;
  padding-top: 1.5rem;
  padding-bottom: 3rem;
  padding-left: clamp(1rem, 3vw, 2.5rem);
  padding-right: clamp(1rem, 3vw, 2.5rem);
}}

/* Hero header */
.st-key-hero {{
  position: relative;
  overflow: hidden;
  {hero_bg}
  color: #FFFFFF;
  border-radius: 18px;
  padding: clamp(1.35rem, 3.5vw, 2.2rem);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-left: 6px solid var(--amber);
  box-shadow: 0 14px 34px rgba(18, 36, 23, 0.18);
  margin-bottom: 1.15rem;
}}
{photo_layer}

.st-key-hero h1 {{
  margin: 0 0 0.4rem 0;
  font-size: clamp(1.55rem, 4vw, 2.15rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #FFFFFF;
  line-height: 1.15;
}}

.st-key-hero p {{
  margin: 0;
  color: rgba(246, 244, 238, 0.92);
  font-size: clamp(0.92rem, 2vw, 1.02rem);
  line-height: 1.5;
  max-width: 42rem;
}}

.hero-badge {{
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #FDE6D8;
  background: rgba(217, 107, 39, 0.28);
  border: 1px solid rgba(253, 230, 216, 0.35);
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
  margin-bottom: 0.65rem;
}}

/* Section headings */
h3 {{
  color: var(--moss);
  font-weight: 750;
  font-size: clamp(1.05rem, 2.4vw, 1.2rem);
  letter-spacing: -0.01em;
  margin: 1.5rem 0 0.6rem 0;
}}

/* KPI metric cards — prevent awkward text ellipsis */
div[data-testid="stMetric"] {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.8rem 0.95rem;
  box-shadow: 0 2px 10px rgba(29, 36, 30, 0.04);
  min-width: 0;
}}

div[data-testid="stMetric"] label {{
  color: var(--ink-muted) !important;
  font-weight: 600;
  font-size: 0.82rem !important;
}}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
  color: var(--ink) !important;
  font-weight: 800;
  font-size: clamp(1rem, 1.85vw, 1.55rem) !important;
  white-space: nowrap;
}}

/* Capture form card */
[data-testid="stForm"] {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: clamp(1rem, 3vw, 1.5rem);
  box-shadow: 0 6px 22px rgba(29, 36, 30, 0.05);
}}

[data-testid="stForm"] label p {{
  font-weight: 650;
  color: var(--ink);
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"],
div[data-baseweb="base-input"] {{
  border-radius: 10px !important;
  background: var(--parchment) !important;
}}

.st-key-history-candidate-select [data-testid="stSelectbox"] [role="group"] {{
  background: var(--moss-light) !important;
}}

.st-key-history-candidate-select [data-testid="stSelectbox"] input[role="combobox"] {{
  background: transparent !important;
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] {{
  border-color: var(--border) !important;
}}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"] > div:focus-within {{
  border-color: var(--moss) !important;
  box-shadow: 0 0 0 3px rgba(30, 86, 49, 0.16) !important;
}}

/* Primary submit & action buttons */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {{
  background: var(--amber);
  color: #FFFFFF;
  border: none;
  border-radius: 10px;
  padding: 0.65rem 1.5rem;
  font-weight: 700;
  font-size: 0.96rem;
  transition: background 0.15s ease, transform 0.15s ease;
}}

.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {{
  background: var(--amber-hover);
  color: #FFFFFF;
  transform: translateY(-1px);
  border: none;
}}

.stButton > button:active,
[data-testid="stFormSubmitButton"] > button:active {{
  transform: translateY(0);
}}

/* Match candidate cards */
.st-key-match-0,
.st-key-match-1,
.st-key-match-2,
.st-key-match-3,
.st-key-match-4 {{
  background: var(--surface);
  border-radius: 14px;
  padding: clamp(0.95rem, 2.5vw, 1.25rem);
  margin-bottom: 0.8rem;
  border: 1px solid var(--border);
  box-shadow: 0 4px 16px rgba(29, 36, 30, 0.05);
}}

.st-key-match-0 {{
  border-left: 5px solid var(--amber);
  background: linear-gradient(90deg, rgba(217, 107, 39, 0.04) 0%, var(--surface) 28%);
}}

.rank {{
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.1rem;
  color: #FFFFFF;
  background: var(--moss);
}}

.st-key-match-0 .rank {{
  background: var(--amber);
}}

.st-key-match-0 [data-testid="stProgress"] > div > div {{
  background: var(--amber);
}}

.top-tag {{
  display: inline-block;
  margin-left: 0.45rem;
  padding: 0.12rem 0.55rem;
  font-size: 0.72rem;
  font-weight: 700;
  border-radius: 999px;
  background: rgba(217, 107, 39, 0.14);
  color: var(--amber-hover);
  vertical-align: middle;
}}

.score-box {{
  text-align: right;
}}

.score-val {{
  font-size: clamp(1.2rem, 2.5vw, 1.45rem);
  font-weight: 800;
  color: var(--moss);
  line-height: 1.1;
}}

.st-key-match-0 .score-val {{
  color: var(--amber-hover);
}}

.score-lbl {{
  font-size: 0.78rem;
  color: var(--ink-muted);
}}

.empty {{
  background: var(--surface-muted);
  border-radius: 14px;
  padding: 1.4rem;
  text-align: center;
  color: var(--ink-muted);
  border: 1px dashed #C7BEAA;
}}

.footer {{
  text-align: center;
  color: var(--ink-muted);
  font-size: 0.85rem;
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}}

/* Mobile adjustments */
@media (max-width: 640px) {{
  .stButton > button,
  [data-testid="stFormSubmitButton"] > button {{
    width: 100%;
  }}

  .score-box {{
    text-align: left;
    margin-top: 0.25rem;
  }}
}}
</style>
"""


CSS = build_css()