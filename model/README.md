# Salamander Recapture Matcher (no VIE, no date)

Decides whether a newly captured salamander is **new** or a **recapture**, and returns the **3 closest past animals** with a probability score for each. It never uses the VIE tag or the capture date as model inputs.

## Architecture

Two parts combined at prediction time:

1. **Binary classifier** (`HistGradientBoostingClassifier`, wrapped in a scikit-learn `Pipeline`) predicts `P(recapture)`: 0 = new, 1 = recapture.
2. **Nearest-neighbour matcher** ranks past animals by closeness on standardized measurements, with penalties for a different site or sex.

Final score per candidate:

```
P(this animal) = P(recapture) × similarity_i / Σ similarity
```

```
new capture ──► binary model ──► P(recapture) ──┐
     │                                          ├─► P(recapture) × share ─► top 3
     └──► distance to every past animal ──► similarity share ─┘
```

## Inputs

| Field | Used by | Notes |
|---|---|---|
| `Site` | both | categorical, ordinal-encoded in the classifier |
| `Sex` | both | categorical |
| `Weight` | both | |
| `Tail Length` | both | |
| `Total Length` | both | |
| `SVL` | classifier | computed as `Total Length - Tail Length` |

**Excluded on purpose:**
- `VIE`, `Salamander ID` and `File Name` identify the animal.
- `Notes` leaks the label (for example, it contains "Missing VIE").
- `Year`, `Month` and `DayOfYear` are not used, so the model does not learn from capture date. The date is only used to pick each animal's latest record for the match history.

## Training

- Data: `data/SalamanderData2020-2025(Updated).csv`
- Target: `Recap`
- Split: 80/20 stratified, `random_state=42`
- Classifier: `learning_rate=0.05`, `max_iter=400`, `max_leaf_nodes=15`, `l2_regularization=1.0`, `class_weight="balanced"`, early stopping
- Matcher history: latest record per `Salamander ID`; `StandardScaler` on Weight, Tail Length, Total Length
- Similarity: `exp(-distance / 2)`, where distance is Euclidean plus `site_pen` (1.0) and `sex_pen` (1.0)

## Outputs

`find_matches(site, sex, weight, tail, total, k=3)` returns a DataFrame with `Rank`, `Salamander ID`, `Site`, `Sex`, measurements, `Date`, `Year` (display only), `Similarity` and `P(this animal)`. It also sets:

- `attrs["p_recapture"]`: probability the animal was seen before
- `attrs["verdict"]`: `likely recapture` (p ≥ 0.5) or `likely new animal`

## Metrics

Reported on the held-out test split: accuracy, precision, recall, F1 and a confusion matrix. Fill in after running the notebook:

| Metric | Value |
|---|---|
| Accuracy | 0.6760 |
| Precision |0.5984 |
| Recall |0.6340 |
| F1 | 0.6157 |

## Files

- `binary_plus_matcher.joblib`: dict with `model` (pipeline), `hist` (history table) and `scaler`

```python
import joblib
bundle = joblib.load("binary_plus_matcher.joblib")
model, hist, scaler = bundle["model"], bundle["hist"], bundle["scaler"]
```

## Limitations

- Similarity share is not calibrated; use `Rank` for ordering and `P(recapture)` for the new-or-seen decision.
- Scores shrink as the history grows because similarity is spread across more animals.
- Without VIE or date, matching relies on measurements, site and sex, so expect lower accuracy than the VIE-based model.