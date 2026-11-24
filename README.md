# Salamander Match Finder (CMPSC 445, Fall 2026)

A Streamlit web frontend for the salamander recapture project. Enter a new
capture's **Site, Sex, Weight, Tail Length and Total Length** and the app returns
the **three closest salamanders** already on record, each with a similarity score.


## Quick start

```bash
# from the repo root
python -m venv .venv
source .venv/bin/activate        
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The app opens at <http://localhost:8501>.

## Using the app

1. Pick a **Site** (dropdown; you can also type to filter) and a **Sex**.
2. Type the **Weight**, **Tail Length** and **Total Length**.
3. Press **Find closest matches**.
4. The three best matches appear as cards: rank, Salamander ID, site, sex,
   measurements, last-seen date, and a similarity bar.

Use the same units as the dataset (weights run roughly 7 to 43, lengths roughly
6 to 24). Hover the `?` on each field to see the exact range in the records.

## Project layout

```
.
├── README.md
├── requirements.txt
├── .streamlit/config.toml     # theme colors and server settings
├── app/
│   ├── streamlit_app.py       # page layout and form
│   ├── matcher.py             # loads data/history.csv, ranks matches
│   └── styles.py              # earthy CSS (cards, buttons, rounded inputs)
├── data/                      # raw data, history.csv, model metrics
├── model/                     # recapture_model.joblib + model README
├── notebooks/
└── src/
```

## How matching works

`app/matcher.py` exposes one function, `Matcher.find_matches(query, k=3)`:

- Records come from `data/history.csv`. A handful of impossible Total Length
  values (for example `5562`) are repaired as `SVL + Tail Length`.
- Weight, Tail Length and Total Length are standardized and compared by
  Euclidean distance.
- A small penalty is added when Sex or Site differs from the query.
- Results are de-duplicated so each Salamander ID appears once (its closest
  record), then the top 3 are returned.
- Similarity is `100 × exp(−distance / 2)`. It is a relative closeness score,
  **not** a probability that two records are the same animal.

## Customizing the theme

- Global colors and fonts: `.streamlit/config.toml`
- Cards, buttons, corner radii, and the hero banner: `app/styles.py`
  (`GREEN`, `ORANGE`, `CREAM` constants at the top)

## Data

`data/history.csv` holds 2,870 captures (2020 to 2025) across five sites:
AMIC, Bayfront, Burke, FieldPonds and Golf.
