# New-vs-Recapture Flagger

CSV-first model that decides whether a newly captured salamander looks **new** or **already recorded**. Photos are an optional extra and are not used here.

## What it is

A gradient-boosted classifier (`HistGradientBoostingClassifier`) that predicts, from CSV fields only, whether a captured salamander was recorded earlier (recapture) or is a new animal.

## Inputs

One new record (numeric fields may be NaN) plus the history.

| Field | Description |
|---|---|
| `Site` | Capture site |
| `VIE` | 4-colour tag, e.g. `"YYPR"` |
| `Sex` | Sex |
| `SVL` | Snout-vent length |
| `Weight` | Weight |
| `t` | Capture date (`pandas.Timestamp`) |

`history` is a DataFrame of all earlier records with the same columns plus `Salamander ID`, `Date` and `Year`, and a parsed `t` column.

## Outputs

A JSON-serialisable dict:

| Key | Meaning |
|---|---|
| `label` | `"recapture"`, `"new"` or `"review"` (`review` = unsure, ask a person) |
| `p_recapture` | Probability (0-1) that the animal was seen before |
| `candidates` | Up to 5 past records with the same Site and a VIE within one colour, to confirm |

## How it decides

Features come from earlier records only: how many have the same VIE (exact or one colour off) at the same site, days since the closest match, sex match, and SVL and weight change.

`p >= hi` gives `recapture`, `p <= lo` gives `new`, otherwise `review`. The thresholds are saved with the model.

## Files written

| File | Contents |
|---|---|
| `recapture_model.joblib` | Model, feature list and thresholds |
| `metrics_summary.csv` | CV metrics (AUC, accuracy, precision/recall, auto-decided share) |
| `metrics_confusion.csv` | Flag vs true `Recap` counts |
| `history.csv` | Record history used by the app for lookups |

## Use in the app

```python
history = pd.read_csv("history.csv", parse_dates=["t"])
result = flag_new_animal(
    {"Site": "Golf", "VIE": "PBOB", "Sex": "F", "SVL": 6.9, "Weight": 14.2,
     "t": pd.Timestamp("2026-03-12")}, history)
# result = {"label", "p_recapture", "candidates"}; the app's MCP tool can return it as-is.
```

- Show `label` and `p_recapture`.
- If `recapture` or `review`, show `candidates` so the user can pick the matching ID.

## Adding new salamanders (no retraining)

The model stores no animals. It scores each record against `history.csv`, so a new capture only needs to be appended to the history. The next check sees it immediately.

```python
def add_capture(record, salamander_id, recapture, path="history.csv"):
    t = pd.Timestamp(record["t"])
    row = {"Date": t.strftime("%d-%b"), "Year": t.year, "Salamander ID": salamander_id,
           "Site": record["Site"], "Sex": record.get("Sex"), "Weight": record.get("Weight"),
           "VIE": str(record["VIE"]).upper().strip(), "Recap": int(recapture),
           "SVL": record.get("SVL"), "t": t}
    pd.concat([pd.read_csv(path), pd.DataFrame([row])], ignore_index=True).to_csv(path, index=False)
```

Call it after the user confirms the ID (an existing ID for a recapture, a new ID otherwise), then reload `history` with `pd.read_csv("history.csv", parse_dates=["t"])`.

Re-run the training cell only to refresh the saved thresholds and model, for example after many new captures. It is optional and is not needed for new animals to be recognised.

## Caveats

- Scored against the CSV's own `Recap` flag, not verified identity.
- `Salamander ID` is **not** used as a feature because IDs are not stable.
- CV is random over rows, although the features are time-causal.
- Append only confirmed captures. A wrong VIE or ID in `history.csv` will mislead later checks.
