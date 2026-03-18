"""
lib/common/common_cleaning.py
Utilitaires partagés de nettoyage de données.
"""

import re
import unicodedata
import numpy as np
import pandas as pd
from typing import List, Tuple


AGE_TRANCHE_MIDPOINTS = {
    "20-30 ans": 25.0,
    "31-40 ans": 35.0,
    "41-50 ans": 45.0,
    "51-60 ans": 55.0,
    "51 ans et plus": 55.0,
    "61-70 ans": 65.0,
}


# ─── Normalisation texte ────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """Normalise une chaîne : minuscules, sans accents, espaces simples."""
    t = unicodedata.normalize("NFKD", str(text))
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.lower().strip()
    t = re.sub(r"[\u2018\u2019\u201a\u201b\u2032\u0060\u00b4]", "'", t)
    t = re.sub(r"\s+", " ", t)
    return t


def normalize_col(text: str) -> str:
    """Normalisation plus agressive pour matching de colonnes (sans accents, sans ponctuation)."""
    t = unicodedata.normalize("NFD", str(text))
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    t = t.lower().strip()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# ─── Suppression PII ────────────────────────────────────────────────────────

PII_PATTERNS = [
    r"\bnom\b", r"\bprenom", r"\be[- ]?mail\b", r"\bmail\b", r"\bcourriel\b",
    r"\btelephone\b", r"\btel\b", r"\bphone\b", r"\bcommentaire",
    r"\bobservation", r"\bremarque", r"\bnumero\b",
]


def clean_pii(df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """Supprime les colonnes PII et celles avec >50% de valeurs manquantes."""
    out = df.copy()
    ops: List[str] = []

    dropped = []
    for col in list(out.columns):
        nc = normalize_col(col)
        if any(re.search(p, nc) for p in PII_PATTERNS) or \
                re.match(r"^#\s*$|^unnamed", str(col).strip(), re.I):
            out = out.drop(columns=[col])
            dropped.append(str(col))
    if dropped:
        ops.append(f"Colonnes PII supprimées ({len(dropped)}): " + ", ".join(dropped))

    miss = out.isna().mean()
    to_drop = miss[miss > 0.5].index.tolist()
    if to_drop:
        out = out.drop(columns=to_drop)
        ops.append("Colonnes >50% manquants supprimées: " + ", ".join(str(c) for c in to_drop))

    log = "Nettoyage appliqué:\n- " + "\n- ".join(ops) if ops else "Aucune opération appliquée."
    return out, log


# ─── Enrichissement socio-démographique ─────────────────────────────────────

def find_col_by_pattern(columns: List[str], patterns: List[str]) -> str | None:
    """Trouve la première colonne dont le nom normalisé matche un des patterns regex."""
    for col in columns:
        nc = normalize_col(col)
        for pat in patterns:
            if re.search(pat, nc):
                return col
    return None


def find_age_col(df: pd.DataFrame) -> str | None:
    """Détecte la colonne d'âge numérique."""
    for col in df.columns:
        nc = normalize_col(col)
        if "tranche" in nc:
            continue
        if re.search(r"\bage\b", nc):
            s = pd.to_numeric(df[col], errors="coerce")
            if not s.dropna().empty:
                return col
    return None


def find_age_tranche_col(df: pd.DataFrame) -> str | None:
    """Détecte une colonne de tranche d'âge, brute ou déjà harmonisée."""
    if "Tranche_age" in df.columns:
        return "Tranche_age"
    return find_col_by_pattern(list(df.columns), [r"tranche.*age"])


def age_tranche_to_numeric(series: pd.Series) -> pd.Series:
    """Convertit des tranches d'âge en âge approximatif via midpoint."""
    normalized_map = {normalize_text(k): v for k, v in AGE_TRANCHE_MIDPOINTS.items()}

    def _parse(value):
        key = normalize_text(value)
        if key in normalized_map:
            return normalized_map[key]

        match = re.search(r"(\d{1,2})\s*[-a]\s*(\d{1,2})", key)
        if match:
            low = float(match.group(1))
            high = float(match.group(2))
            return (low + high) / 2

        plus_match = re.search(r"(\d{1,2}).*(plus|et plus)", key)
        if plus_match:
            return float(plus_match.group(1)) + 4.0

        return np.nan

    return series.map(_parse).astype(float)


def get_age_series(df: pd.DataFrame) -> pd.Series:
    """Retourne une série d'âges numériques réels ou estimés depuis une tranche."""
    age_col = find_age_col(df)
    if age_col:
        return pd.to_numeric(df[age_col], errors="coerce")

    tranche_col = find_age_tranche_col(df)
    if tranche_col:
        return age_tranche_to_numeric(df[tranche_col].astype(str).str.strip())

    return pd.Series(np.nan, index=df.index, dtype=float)


def compute_average_age(df: pd.DataFrame) -> float:
    """Calcule l'âge moyen avec fallback sur les tranches d'âge."""
    ages = get_age_series(df).dropna()
    return round(float(ages.mean()), 1) if not ages.empty else 0.0


def enrich_sociodem(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute tranches d'âge, ancienneté et IMC si les colonnes sources existent."""
    df = df.copy()
    cols = list(df.columns)

    # Tranche d'âge
    age_col = find_age_col(df)
    if age_col and "Tranche_age" not in df.columns:
        age_num = pd.to_numeric(df[age_col], errors="coerce")
        df["Tranche_age"] = pd.cut(
            age_num, bins=[0, 30, 40, 50, np.inf],
            labels=["20-30 ans", "31-40 ans", "41-50 ans", "51 ans et plus"],
            right=True,
        )
    elif "Tranche_age" not in df.columns:
        tranche_col = find_age_tranche_col(df)
        if tranche_col:
            df = remap_age_tranche(df, tranche_col)

    # Tranche ancienneté
    anc_col = find_col_by_pattern(cols, [r"anciennet"])
    if anc_col and "Tranche_anciennete" not in df.columns:
        anc_num = pd.to_numeric(df[anc_col], errors="coerce")
        df["Tranche_anciennete"] = pd.cut(
            anc_num, bins=[-1, 2, 5, 10, 20, np.inf],
            labels=["0-2 ans", "3-5 ans", "6-10 ans", "11-20 ans", "21 ans et +"],
        )

    # IMC
    poids_col = find_col_by_pattern(cols, [r"\bpoids\b"])
    taille_col = find_col_by_pattern(cols, [r"\btaille\b"])
    if poids_col and taille_col:
        poids = pd.to_numeric(df[poids_col], errors="coerce")
        taille = pd.to_numeric(df[taille_col], errors="coerce")
        if not taille[taille > 0].empty and float(taille[taille > 0].median()) > 3:
            taille = taille / 100.0
        imc = (poids / taille ** 2).replace([np.inf, -np.inf], np.nan)
        df["IMC"] = imc
        df["Categorie_IMC"] = pd.cut(
            imc, bins=[0, 18.5, 25, 30, 200],
            labels=["Insuffisance pondérale", "Corpulence normale", "Surpoids", "Obésité"],
            include_lowest=True,
        )
        df["IMC_binaire"] = np.where(
            df["Categorie_IMC"].isna(), None,
            np.where(
                df["Categorie_IMC"].isin(["Insuffisance pondérale", "Corpulence normale"]),
                "Normal",
                "Surpoids/Obésité",
            ),
        )
    return df


# ─── Helpers génériques ─────────────────────────────────────────────────────

def clip_likert(series: pd.Series, low: int = 1, high: int = 4) -> pd.Series:
    """Convertit en numérique et clip sur [low, high]."""
    s = pd.to_numeric(series, errors="coerce")
    return s.where(s.between(low, high))


def invert_items(df: pd.DataFrame, cols: List[str], low: int = 1, high: int = 4) -> pd.DataFrame:
    """Inverse les items sur l'échelle Likert."""
    avail = [c for c in cols if c in df.columns]
    if avail:
        df[avail] = (low + high) - df[avail]
    return df

def remap_age_tranche(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Remplace les tranches d'âge par des labels plus lisibles."""
    mapping = {
        "20-30 ans":   "20-30 ans",
        "20 - 30 ans": "20-30 ans",
        "31 - 40 ans": "31-40 ans",
        "31-40 ans":   "31-40 ans",
        "41 - 50 ans": "41-50 ans",
        "41-50 ans":   "41-50 ans",
        "51 - 60 ans": "51-60 ans",
        "51-60 ans":   "51-60 ans",
        "61 - 70 ans": "61-70 ans",
        "61-70 ans":   "61-70 ans",
        "51 ans et plus": "51 ans et plus",
    }
    if col in df.columns:
        normalized_map = {normalize_text(k): v for k, v in mapping.items()}
        src = df[col].astype(str).str.strip()
        df["Tranche_age"] = src.map(lambda v: normalized_map.get(normalize_text(v), v))
    return df

def compute_group_score(
    df: pd.DataFrame,
    suffix: str,
    multiplier: int = 1,
) -> pd.Series:
    """Calcule le score moyen pondéré pour un groupe d'items (suffixe Q*_suffix)."""
    cols = [c for c in df.columns if c.endswith(f"_{suffix}")]
    if not cols:
        return pd.Series(np.nan, index=df.index, name=f"{suffix}_score")
    ssum = df[cols].sum(axis=1, skipna=True)
    n_ans = df[cols].notna().sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        score = ssum / n_ans.replace(0, np.nan) * len(cols) * multiplier
    return score.where(n_ans > 0, np.nan).rename(f"{suffix}_score")
