"""
lib/questionnaires/karasek/visualizations.py
Générateur de visualisations matplotlib/seaborn pour le rapport Karasek.
Toutes les méthodes retournent des bytes PNG (prêts pour Word ou ZIP).
"""

import io
import textwrap
import warnings
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

from .config import THRESHOLDS, SCORE_LABELS, KARASEK_COLORS

# ─── Palette Wave-CI ─────────────────────────────────────────────────────────
ACCENT      = "#38A3E8"
ORANGE      = "#F97316"
GREEN       = "#22C55E"
RED         = "#EF4444"
SLATE       = "#94A3B8"
DARK        = "#0F2340"
BG          = "#FAFCFF"
GRID_COLOR  = "#EDF5FD"
TEXT_MID    = "#4E6A88"

QUAD_COLORS = {
    "Actif":   GREEN,
    "Detendu": ACCENT,
    "Détendu": ACCENT,
    "Tendu":   RED,
    "Passif":  SLATE,
}

BAR_PALETTE = [ACCENT, ORANGE, GREEN, RED, "#A78BFA", "#06B6D4", "#FB923C", "#84CC16"]

HOMME_COLOR = "#4472C4"
FEMME_COLOR = "#E91E8C"


def _fig_bytes(fig) -> bytes:
    """Sérialise une figure matplotlib en PNG bytes et ferme la figure."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def _base_style(ax, title: str = "", xlabel: str = "", ylabel: str = "",
                title_wrap: int = 60):
    ax.set_facecolor(BG)
    ax.figure.patch.set_facecolor("white")
    ax.grid(True, color=GRID_COLOR, linewidth=0.8, axis="x")
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#D6E8F7")
    ax.tick_params(colors=TEXT_MID, labelsize=9)
    if title:
        ax.set_title("\n".join(textwrap.wrap(title, title_wrap)),
                     fontsize=13, fontweight="bold", color=DARK, pad=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10, color=TEXT_MID, labelpad=8)
    if ylabel:
        ax.set_ylabel("\n".join(textwrap.wrap(ylabel, 22)),
                      fontsize=10, color=TEXT_MID, labelpad=8)


# =============================================================================
# 1 — PYRAMIDE DES ÂGES
# =============================================================================

def plot_age_pyramid(df: pd.DataFrame, company: str = "") -> Optional[bytes]:
    """Pyramide des âges Homme/Femme par tranche."""
    if "Tranche_age" not in df.columns or "Genre" not in df.columns:
        return None
    data = df[["Tranche_age", "Genre"]].dropna()
    if data.empty:
        return None

    age_order = ["20-30 ans", "31-40 ans", "41-50 ans", "51 ans et plus"]
    age_order  = [a for a in age_order if a in data["Tranche_age"].unique()]
    if not age_order:
        age_order = sorted(data["Tranche_age"].unique())

    ct = pd.crosstab(data["Tranche_age"], data["Genre"]).reindex(age_order, fill_value=0)
    totaux = ct.sum(axis=0)
    ct_pct = ct.div(totaux.replace(0, np.nan), axis=1).fillna(0) * 100

    h_vals = ct_pct.get("Homme", pd.Series(0.0, index=age_order))
    f_vals = ct_pct.get("Femme", pd.Series(0.0, index=age_order))
    h_n    = ct.get("Homme", pd.Series(0, index=age_order))
    f_n    = ct.get("Femme", pd.Series(0, index=age_order))

    max_val = max(h_vals.max(), f_vals.max(), 1) * 1.2
    seuil   = max_val * 0.15

    fig, ax = plt.subplots(figsize=(9, max(4, len(age_order) * 1.2 + 1.5)))

    bars_h = ax.barh(age_order, -h_vals, color=HOMME_COLOR, edgecolor="white",
                     height=0.6, label="Homme", zorder=3)
    bars_f = ax.barh(age_order, f_vals,  color=FEMME_COLOR, edgecolor="white",
                     height=0.6, label="Femme", zorder=3)

    def _annotate(bars, vals, ns, side):
        for bar, pct, n in zip(bars, vals, ns):
            if pct <= 0:
                continue
            bw  = abs(bar.get_width())
            yc  = bar.get_y() + bar.get_height() / 2
            lbl = f"{pct:.1f}%\n(n={n})"
            if bw >= seuil:
                ax.text(bar.get_x() + bar.get_width() / 2, yc, lbl,
                        ha="center", va="center", fontsize=8,
                        fontweight="bold", color="white", zorder=4)
            else:
                xp = bar.get_x() - 0.4 if side == "left" else bar.get_x() + bar.get_width() + 0.4
                ha = "right" if side == "left" else "left"
                ax.text(xp, yc, lbl, ha=ha, va="center",
                        fontsize=8, fontweight="bold", color=DARK, zorder=4)

    _annotate(bars_h, h_vals, h_n, "left")
    _annotate(bars_f, f_vals, f_n, "right")

    ax.axvline(0, color=DARK, linewidth=0.9)
    ax.set_xlim(-max_val, max_val)
    ticks = [t for t in ax.get_xticks()]
    ax.set_xticklabels([f"{abs(t):.0f}%" for t in ticks], fontsize=9)
    ax.set_facecolor(BG)
    ax.figure.patch.set_facecolor("white")
    ax.grid(True, color=GRID_COLOR, linewidth=0.8, axis="x", zorder=0)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#D6E8F7")

    suffix = f" — {company}" if company else ""
    ax.set_title(f"Pyramide des âges{suffix}",
                 fontsize=13, fontweight="bold", color=DARK, pad=14)
    ax.set_xlabel("% au sein de chaque genre", fontsize=10, color=TEXT_MID)
    ax.set_ylabel("Tranche d'âge", fontsize=10, color=TEXT_MID)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
    fig.tight_layout()
    return _fig_bytes(fig)


# =============================================================================
# 2 — BARPLOT SIMPLE (variable catégorielle)
# =============================================================================

def plot_categorical(df: pd.DataFrame, col: str,
                     title: str = "", company: str = "") -> Optional[bytes]:
    """Barplot horizontal d'une variable catégorielle."""
    if col not in df.columns:
        return None
    data = df[col].dropna()
    if data.empty:
        return None

    cnt = data.value_counts()
    mods = list(cnt.index)
    pcts = (cnt / cnt.sum() * 100).round(1)

    fig_h = max(3.5, len(mods) * 0.7 + 1.5)
    fig, ax = plt.subplots(figsize=(9, fig_h))
    colors = [BAR_PALETTE[i % len(BAR_PALETTE)] for i in range(len(mods))]

    bars = ax.barh(mods, pcts, color=colors, edgecolor="white", height=0.6, zorder=3)
    for bar, pct, n in zip(bars, pcts, cnt):
        if pct > 0:
            ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                    f"{pct:.1f}%  (n={n})", va="center", ha="left",
                    fontsize=9, fontweight="bold", color=DARK)

    ax.set_xlim(0, min(pcts.max() * 1.35, 120))
    lbl = title or col
    suffix = f" — {company}" if company else ""
    _base_style(ax, title=f"Répartition : {lbl}{suffix}",
                xlabel="Pourcentage (%)", ylabel=lbl)
    fig.tight_layout()
    return _fig_bytes(fig)


# =============================================================================
# 3 — STACKED BAR (croisement)
# =============================================================================

def plot_stacked_bar(df: pd.DataFrame, x_col: str, hue_col: str,
                     company: str = "") -> Optional[bytes]:
    """Barplot empilé 100% pour un croisement de deux variables."""
    if x_col not in df.columns or hue_col not in df.columns:
        return None
    tmp = df[[x_col, hue_col]].dropna()
    if tmp.empty:
        return None

    ct  = pd.crosstab(tmp[x_col], tmp[hue_col])
    pct = ct.div(ct.sum(axis=1), axis=0) * 100
    cats = list(pct.columns)

    # Couleurs contextuelles
    COLOR_MAP = {**QUAD_COLORS,
                 "Élevé": GREEN, "Eleve": GREEN, "Faible": RED,
                 "Satisfaisant": GREEN, "Mitigé": ORANGE, "Insatisfaisant": RED,
                 "Présent": RED, "Absent": GREEN,
                 "Bas": GREEN, "Modéré": ORANGE}
    colors = [COLOR_MAP.get(str(c), BAR_PALETTE[i % len(BAR_PALETTE)])
              for i, c in enumerate(cats)]

    fig_h = max(3.5, len(pct.index) * 0.8 + 2)
    fig, ax = plt.subplots(figsize=(11, fig_h))

    left = np.zeros(len(pct.index))
    for i, cat in enumerate(cats):
        vals = pct[cat].values
        ns   = ct[cat].values
        bars = ax.barh(list(pct.index), vals, left=left,
                       color=colors[i], edgecolor="white",
                       height=0.65, label=str(cat), zorder=3)
        for bar, v, n in zip(bars, vals, ns):
            if v >= 5:
                xc = bar.get_x() + bar.get_width() / 2
                yc = bar.get_y() + bar.get_height() / 2
                ax.text(xc, yc, f"{v:.0f}%\n(n={n})",
                        ha="center", va="center", fontsize=8,
                        fontweight="bold", color="white", zorder=4)
        left += vals

    ax.set_xlim(0, 100)
    suffix = f" — {company}" if company else ""
    _base_style(ax,
                title=f"{x_col} × {hue_col}{suffix}",
                xlabel="Pourcentage (%)", ylabel=x_col)
    ax.legend(title=hue_col, bbox_to_anchor=(1.01, 1), loc="upper left",
              fontsize=8, title_fontsize=8, framealpha=0.9)
    fig.tight_layout()
    return _fig_bytes(fig)


# =============================================================================
# 4 — SCATTER KARASEK (grille MAPP)
# =============================================================================

def plot_karasek_scatter(df: pd.DataFrame, company: str = "") -> Optional[bytes]:
    """Scatter Dem_score × Lat_score coloré par quadrant théorique."""
    quad_col = "Karasek_quadrant_theoretical"
    need = ["Dem_score", "Lat_score", quad_col]
    if any(c not in df.columns for c in need):
        return None
    data = df[need].dropna()
    if data.empty:
        return None

    DT = THRESHOLDS["Dem_score"]
    LT = THRESHOLDS["Lat_score"]

    xmn, xmx = data["Dem_score"].min(), data["Dem_score"].max()
    ymn, ymx = data["Lat_score"].min(), data["Lat_score"].max()
    mx, my   = max((xmx - xmn) * 0.06, 0.5), max((ymx - ymn) * 0.06, 0.5)
    xlo, xhi = xmn - mx, xmx + mx
    ylo, yhi = ymn - my, ymx + my

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_facecolor(BG); fig.patch.set_facecolor("white")

    # Zones de fond
    za = 0.07
    ax.fill_between([DT, xhi], LT, yhi, color=GREEN,  alpha=za)
    ax.fill_between([xlo, DT], LT, yhi, color=ACCENT, alpha=za)
    ax.fill_between([DT, xhi], ylo, LT, color=RED,    alpha=za)
    ax.fill_between([xlo, DT], ylo, LT, color=SLATE,  alpha=za)

    # Lignes de seuil
    ax.axvline(DT, color=ORANGE, linestyle="--", linewidth=1.4, alpha=0.6)
    ax.axhline(LT, color=ORANGE, linestyle=":",  linewidth=1.4, alpha=0.6)

    # Points par quadrant
    quad_order = ["Actif", "Detendu", "Tendu", "Passif"]
    qmap_display = {"Actif": "Actif", "Detendu": "Détendu",
                    "Détendu": "Détendu", "Tendu": "Tendu", "Passif": "Passif"}
    for quad in quad_order:
        sub = data[data[quad_col] == quad]
        if sub.empty:
            continue
        pct = len(sub) / len(data) * 100
        ax.scatter(sub["Dem_score"], sub["Lat_score"],
                   c=QUAD_COLORS.get(quad, SLATE), s=55, alpha=0.78,
                   edgecolors="white", linewidths=0.5, zorder=3,
                   label=f"{qmap_display.get(quad, quad)}  {pct:.1f}%  (n={len(sub)})")

    # Labels quadrants
    for quad, (qx, qy, ha, va) in {
        "Actif":   (xhi - mx * 0.5, yhi - my * 0.5, "right", "top"),
        "Detendu": (xlo + mx * 0.5, yhi - my * 0.5, "left",  "top"),
        "Tendu":   (xhi - mx * 0.5, ylo + my * 0.5, "right", "bottom"),
        "Passif":  (xlo + mx * 0.5, ylo + my * 0.5, "left",  "bottom"),
    }.items():
        ax.text(qx, qy, quad.upper(),
                color=QUAD_COLORS.get(quad, SLATE),
                fontsize=9, fontweight="bold",
                ha=ha, va=va, alpha=0.4, zorder=2)

    ax.set_xlim(xlo, xhi); ax.set_ylim(ylo, yhi)
    ax.grid(True, color=GRID_COLOR, linewidth=0.7, zorder=0)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color("#D6E8F7")
    ax.tick_params(colors=TEXT_MID, labelsize=9)

    suffix = f" — {company}" if company else ""
    ax.set_title(f"Grille MAPP — Demande × Latitude décisionnelle{suffix}",
                 fontsize=13, fontweight="bold", color=DARK, pad=14)
    ax.set_xlabel("Demande psychologique", fontsize=10, color=TEXT_MID)
    ax.set_ylabel("Latitude décisionnelle", fontsize=10, color=TEXT_MID)
    ax.legend(title="Quadrant de Karasek", bbox_to_anchor=(1.01, 1),
              loc="upper left", fontsize=8, title_fontsize=9, framealpha=0.9)
    fig.tight_layout()
    return _fig_bytes(fig)


# =============================================================================
# 5 — HEATMAP PAR DIRECTION
# =============================================================================

def plot_karasek_heatmap(df: pd.DataFrame, company: str = "") -> Optional[bytes]:
    """Heatmap des quadrants Karasek par direction."""
    quad_col = "Karasek_quadrant_theoretical"
    dir_col  = next((c for c in df.columns
                     if c.strip().lower() == "direction"), None)
    if not dir_col or quad_col not in df.columns:
        return None

    ct = pd.crosstab(df[dir_col], df[quad_col], normalize="index") * 100
    quads = ["Tendu", "Actif", "Passif", "Detendu"]
    for q in quads:
        if q not in ct.columns:
            ct[q] = 0.0
    ct = ct[quads].sort_values("Tendu", ascending=True)

    cmaps = {
        "Tendu":   ["#FFFFFF", RED],
        "Actif":   ["#FFFFFF", ACCENT],
        "Passif":  ["#FFFFFF", SLATE],
        "Detendu": ["#FFFFFF", GREEN],
    }
    quad_labels = {"Tendu": "Tendu", "Actif": "Actif",
                   "Passif": "Passif", "Detendu": "Détendu"}

    fig_h = max(3, 1 + len(ct) * 0.45)
    fig, axes = plt.subplots(1, 4, figsize=(18, fig_h), sharey=True)
    fig.patch.set_facecolor("white")

    for ax, q in zip(axes, quads):
        cmap = LinearSegmentedColormap.from_list(q, cmaps[q])
        sns.heatmap(ct[[q]], ax=ax, cmap=cmap, vmin=0, vmax=60,
                    annot=True, fmt=".0f",
                    annot_kws={"size": 9, "weight": "bold", "color": DARK},
                    linewidths=0.5, linecolor="#F0F7FF", cbar=False)
        ax.set_title(quad_labels[q], fontsize=11, fontweight="bold",
                     color=cmaps[q][1], pad=6)
        ax.set_xlabel("%", fontsize=8, color=TEXT_MID)
        ax.set_ylabel("" if q != "Tendu" else "Direction", fontsize=9)
        ax.tick_params(axis="y", labelsize=8, colors=TEXT_MID)
        ax.tick_params(axis="x", bottom=False, labelbottom=False)
        for spine in ax.spines.values():
            spine.set_visible(False)

    suffix = f" — {company}" if company else ""
    fig.suptitle(f"Répartition Karasek par Direction{suffix} (trié par tension ↑)",
                 fontsize=12, fontweight="bold", color=DARK, y=1.02)
    fig.tight_layout()
    return _fig_bytes(fig)


# =============================================================================
# 6 — RADAR DES SCORES RH
# =============================================================================

def plot_rh_radar(df: pd.DataFrame, metrics: dict, company: str = "") -> Optional[bytes]:
    """
    Radar matplotlib des dimensions RH (% niveau élevé).
    Utilise les metrics déjà calculés par KarasekAnalytics.
    """
    rh = metrics.get("rh_scores", {})
    if not rh:
        return None

    labels = [v["label"] for v in rh.values()]
    vals   = [v["pct"]   for v in rh.values()]
    if len(labels) < 3:
        return None

    N     = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    vals_c  = vals  + [vals[0]]
    angles_c = angles + [angles[0]]
    labels_c = labels + [labels[0]]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})
    fig.patch.set_facecolor("white")
    ax.set_facecolor(BG)

    # Référence 50%
    ax.plot(angles_c, [50] * (N + 1),
            color=ORANGE, linestyle="--", linewidth=1.2, alpha=0.45)
    ax.fill(angles, [50] * N, color=ORANGE, alpha=0.03)

    # Données
    ax.plot(angles_c, vals_c, color=ACCENT, linewidth=2.2, zorder=3)
    ax.fill(angles, vals, color=ACCENT, alpha=0.15, zorder=2)
    ax.scatter(angles, vals, color=ACCENT, s=50, zorder=4,
               edgecolors="white", linewidths=1.5)

    ax.set_xticks(angles)
    ax.set_xticklabels(
        ["\n".join(textwrap.wrap(l, 12)) for l in labels],
        fontsize=8, color=DARK
    )
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=7, color=TEXT_MID)
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.8)
    ax.xaxis.grid(True, color=GRID_COLOR, linewidth=0.8)
    ax.spines["polar"].set_color("#D6E8F7")

    suffix = f" — {company}" if company else ""
    ax.set_title(f"Radar des dimensions organisationnelles{suffix}\n(% niveau élevé)",
                 fontsize=11, fontweight="bold", color=DARK, pad=22)

    # Légende manuelle
    handles = [
        mpatches.Patch(color=ACCENT, alpha=0.7, label="Score observé"),
        plt.Line2D([0], [0], color=ORANGE, linestyle="--", linewidth=1.2,
                   label="Référence 50%"),
    ]
    ax.legend(handles=handles, loc="lower right",
              bbox_to_anchor=(1.25, -0.05), fontsize=8, framealpha=0.9)

    fig.tight_layout()
    return _fig_bytes(fig)


# =============================================================================
# 7 — BARRES DE STRAIN (Job Strain / Iso-Strain)
# =============================================================================

def plot_strain_bars(df: pd.DataFrame, company: str = "") -> Optional[bytes]:
    """Barplot horizontal Job Strain + Iso-Strain + quadrants."""
    strain_cols = {
        "Job Strain":  "Job_strain_theoretical",
        "Iso-Strain":  "Iso_strain_theoretical",
    }
    quad_col = "Karasek_quadrant_theoretical"

    rows = []
    for label, col in strain_cols.items():
        if col in df.columns:
            v = df[col].dropna()
            n = int((v == "Présent").sum())
            rows.append({"label": label, "pct": n / len(v) * 100 if len(v) else 0, "n": n})

    if quad_col in df.columns:
        v = df[quad_col].dropna()
        tv = len(v)
        for quad, color in [("Tendu", RED), ("Actif", GREEN),
                             ("Passif", SLATE), ("Detendu", ACCENT)]:
            n = int(v.isin([quad, f"Dé{quad[1:]}" if quad == "Detendu" else quad]).sum())
            rows.append({"label": quad, "pct": n / tv * 100 if tv else 0, "n": n})

    if not rows:
        return None

    df_r   = pd.DataFrame(rows)
    labels = df_r["label"].tolist()
    pcts   = df_r["pct"].tolist()
    ns     = df_r["n"].tolist()

    color_map = {"Job Strain": RED, "Iso-Strain": ORANGE,
                 "Actif": GREEN, "Detendu": ACCENT,
                 "Tendu": RED,   "Passif": SLATE}
    colors = [color_map.get(l, ACCENT) for l in labels]

    fig, ax = plt.subplots(figsize=(9, max(3, len(labels) * 0.75 + 1.2)))
    bars = ax.barh(labels, pcts, color=colors, edgecolor="white",
                   height=0.55, zorder=3)
    for bar, pct, n in zip(bars, pcts, ns):
        ax.text(bar.get_width() + 0.8,
                bar.get_y() + bar.get_height() / 2,
                f"{pct:.1f}%  (n={n})",
                va="center", ha="left", fontsize=9,
                fontweight="bold", color=DARK)

    ax.set_xlim(0, min(max(pcts) * 1.4, 110))
    suffix = f" — {company}" if company else ""
    _base_style(ax, title=f"Prévalence des RPS & Quadrants Karasek{suffix}",
                xlabel="Pourcentage (%)")
    # Ligne de référence 25%
    ax.axvline(25, color=ORANGE, linestyle=":", linewidth=1.2, alpha=0.5)
    ax.text(25.5, ax.get_ylim()[1] * 0.98, "seuil 25%",
            fontsize=7, color=ORANGE, va="top")
    fig.tight_layout()
    return _fig_bytes(fig)


# =============================================================================
# ORCHESTRATEUR — génère toutes les visualisations
# =============================================================================

class KarasekVisualizations:
    """
    Génère l'ensemble des visualisations Karasek.
    Toutes les figures sont retournées en bytes PNG.
    """

    def __init__(self, company: str = ""):
        self.company = company

    def generate_all(self, df: pd.DataFrame, metrics: dict) -> Dict[str, bytes]:
        """
        Retourne un dict {nom_figure: png_bytes}.
        Les valeurs None sont exclues automatiquement.
        """
        generators = {
            "age_pyramid":         lambda: plot_age_pyramid(df, self.company),
            "karasek_scatter":     lambda: plot_karasek_scatter(df, self.company),
            "karasek_heatmap":     lambda: plot_karasek_heatmap(df, self.company),
            "rh_radar":            lambda: plot_rh_radar(df, metrics, self.company),
            "strain_bars":         lambda: plot_strain_bars(df, self.company),
            "genre_barplot":       lambda: plot_categorical(df, "Genre", "Genre", self.company),
            "tranche_age_barplot": lambda: plot_categorical(df, "Tranche_age", "Tranche d'âge", self.company),
            "direction_barplot":   lambda: plot_categorical(df, "Direction", "Direction", self.company) if "Direction" in df.columns else None,
            "csp_barplot":         lambda: plot_categorical(
                df,
                next((c for c in df.columns if "socio" in c.lower() or c == "CSP"), ""),
                "Catégorie socioprofessionnelle", self.company
            ) if any("socio" in c.lower() or c == "CSP" for c in df.columns) else None,
        }

        results = {}
        for name, fn in generators.items():
            try:
                result = fn()
                if result:
                    results[name] = result
            except Exception as e:
                import warnings
                warnings.warn(f"Visualisation '{name}' échouée : {e}")

        return results

    def generate_for_report(self, df: pd.DataFrame, metrics: dict) -> Dict[str, bytes]:
        """
        Sous-ensemble de figures destinées au rapport Word.
        """
        all_figs = self.generate_all(df, metrics)
        report_keys = [
            "karasek_scatter",
            "karasek_heatmap",
            "strain_bars",
            "rh_radar",
            "age_pyramid",
        ]
        return {k: all_figs[k] for k in report_keys if k in all_figs}
