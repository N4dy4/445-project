"""Matching layer for the salamander frontend.

`find_matches(query, k)` is the single function the UI calls. It returns the
top-k closest past records for a set of field measurements.

Swap point: if you later expose a model-side matcher (for example a function in
the notebook that wraps recapture_model.joblib), replace the body of
`find_matches` and keep the same input/output shape; the UI will not change.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = REPO_ROOT / "data" / "history.csv"

NUMERIC = ["Weight", "Tail Length", "Total Length"]
SEX_PENALTY = 1.0   # added to distance when sex differs
SITE_PENALTY = 0.75  # added to distance when site differs
SIMILARITY_SCALE = 2.0  # larger = scores fall off more slowly


def load_history(path: Path = HISTORY_PATH) -> pd.DataFrame:
    """Load history.csv and repair obvious data-entry problems."""
    df = pd.read_csv(path)
    # A few Total Length values are typos (e.g. 5562). Total = SVL + Tail.
    rebuilt = df["SVL"] + df["Tail Length"]
    bad = df["Total Length"].isna() | (df["Total Length"] > 40)
    df.loc[bad, "Total Length"] = rebuilt[bad]
    df["t"] = pd.to_datetime(df["t"], errors="coerce")
    df = df.dropna(subset=NUMERIC + ["Site", "Sex"]).reset_index(drop=True)
    return df


@dataclass
class Matcher:
    history: pd.DataFrame

    def __post_init__(self) -> None:
        self.mean = self.history[NUMERIC].mean()
        self.std = self.history[NUMERIC].std().replace(0, 1)
        self._z = (self.history[NUMERIC] - self.mean) / self.std

    @property
    def sites(self) -> list[str]:
        return sorted(self.history["Site"].unique())

    @property
    def ranges(self) -> dict[str, tuple[float, float]]:
        return {c: (float(self.history[c].min()), float(self.history[c].max())) for c in NUMERIC}

    def find_matches(self, query: dict, k: int = 3) -> pd.DataFrame:
        """Return the k closest distinct salamanders to `query`.

        query keys: Site, Sex, Weight, Tail Length, Total Length.
        """
        q = pd.Series({c: float(query[c]) for c in NUMERIC})
        qz = (q - self.mean) / self.std
        dist = np.sqrt(((self._z - qz) ** 2).sum(axis=1))
        dist = dist + np.where(self.history["Sex"] != query["Sex"], SEX_PENALTY, 0.0)
        dist = dist + np.where(self.history["Site"] != query["Site"], SITE_PENALTY, 0.0)

        out = self.history.assign(_dist=dist.values)
        # One row per Salamander ID: keep the closest record of each animal.
        out = out.sort_values("_dist").drop_duplicates("Salamander ID").head(k).copy()
        out["Similarity"] = (100 * np.exp(-out["_dist"] / SIMILARITY_SCALE)).round(1)
        cols = ["Salamander ID", "Site", "Sex", "Weight", "Tail Length",
                "Total Length", "t", "Similarity"]
        return out[cols].reset_index(drop=True)
