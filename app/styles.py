"""Earthy, soft-edged styling for the Streamlit app."""

GREEN = "#196B24"
ORANGE = "#BF4E14"
CREAM = "#FBF8F1"
SAND = "#EEEBE4"
INK = "#2B2A22"

CSS = f"""
<style>
:root {{
  --green: {GREEN}; --orange: {ORANGE}; --cream: {CREAM};
  --sand: {SAND}; --ink: {INK};
}}
.stApp {{ background: var(--cream); }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ max-width: 920px; padding-top: 2.2rem; padding-bottom: 3rem; }}

/* Hero */
.st-key-hero {{
  background: var(--green); color: #fff; border-radius: 16px;
  padding: 1.8rem 2rem; border-left: 6px solid var(--orange);
}}
.st-key-hero h1 {{ margin: 0 0 .35rem 0; font-size: 2rem; color: #fff; letter-spacing: -.01em; }}
.st-key-hero p {{ margin: 0; opacity: .92; font-size: 1rem; max-width: 34rem; }}

/* Cards */
.card {{
  background: #fff; border-radius: 14px; padding: 1.4rem 1.6rem;
  border: 1px solid #E8E1CF; box-shadow: 0 4px 18px rgba(43,42,34,.05);
}}
h3 {{ color: var(--green); font-weight: 700; font-size: 1.15rem; margin: 1.8rem 0 .6rem 0; }}

/* Form container */
[data-testid="stForm"] {{
  background: #fff; border: 1px solid #E8E1CF; border-radius: 14px;
  padding: 1.4rem 1.6rem; box-shadow: 0 4px 18px rgba(43,42,34,.05);
}}
[data-testid="stForm"] label p {{ font-weight: 600; color: var(--ink); }}

/* Inputs */
div[data-baseweb="select"] > div, div[data-baseweb="input"], div[data-baseweb="base-input"] {{
  border-radius: 8px !important; background: var(--cream) !important;
}}
div[data-baseweb="select"] > div, div[data-baseweb="input"] {{ border-color: #DDD4BD !important; }}
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within {{
  border-color: var(--green) !important; box-shadow: 0 0 0 3px rgba(25,107,36,.15) !important;
}}

/* Orange accent button */
.stButton > button, [data-testid="stFormSubmitButton"] > button {{
  background: var(--orange); color: #fff; border: none; border-radius: 8px;
  padding: .7rem 2rem; font-weight: 700; font-size: 1.02rem;
  box-shadow: none; transition: background .12s ease, transform .12s ease;
}}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{
  background: #A64211; color: #fff; transform: translateY(-1px);
  box-shadow: none; border: none;
}}
.stButton > button:active, [data-testid="stFormSubmitButton"] > button:active {{ transform: translateY(0); }}

/* Match cards */
.st-key-match-0, .st-key-match-1, .st-key-match-2 {{
  background: #fff; border-radius: 14px; padding: 1.1rem 1.3rem; margin-bottom: .75rem;
  border: 1px solid #E8E1CF; box-shadow: 0 4px 18px rgba(43,42,34,.05);
}}
.st-key-match-0 {{ border-left: 4px solid var(--orange); }}
.rank {{
  width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-weight: 800; font-size: 1.3rem; color: #fff; background: var(--green);
}}
.st-key-match-0 .rank {{ background: var(--orange); }}
.st-key-match-0 [data-testid="stProgress"] > div > div {{ background: var(--green); }}

.empty {{
  background: var(--sand); border-radius: 14px; padding: 1.4rem; text-align: center; color: #6B664F;
  border: 1px solid #D6CCB0;
}}
.footer {{ text-align: center; color: #8A846C; font-size: .85rem; margin-top: 2.5rem; }}
</style>
"""
