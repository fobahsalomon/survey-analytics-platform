import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import pandas as pd
import numpy as np
import textwrap
import unicodedata
from typing import Dict, List, Optional, Tuple
import logging

from .config import KarasekConfig

logger = logging.getLogger(__name__)


def _sort_modalities(series: pd.Series, col_name: str, modality_order: Dict) -> List:
    """Tri les modalités selon l'ordre défini dans la config."""
    present = list(series.dropna().unique())
    if col_name in modality_order and modality_order[col_name]:
        ordered = [m for m in modality_order[col_name] if m in present]
        ordered += [m for m in present if m not in ordered]
        return ordered
    return sorted(present, key=str)


class KarasekVisualizer:
    """
    Générateur de graphiques pour le rapport Karasek.
    Utilise UNIQUEMENT les seuils théoriques (*_theoretical).
    """
    
    TITLE_SIZE   = 15
    LABEL_SIZE   = 12
    TICK_SIZE    = 10
    ANNOT_SIZE   = 13
    LEGEND_SIZE  = 10
    TITLE_WRAP   = 60
    YLABEL_WRAP  = 20
    LEGEND_PAD   = 1.05
    RIGHT_MARGIN = 0.78
    STACKED_ANNOT_SIZE   = 13
    STACKED_ANNOT_COLOR  = "white"
    STACKED_ANNOT_WEIGHT = "bold"
    PYRAMID_COLOR_HOMME = "#4472C4"
    PYRAMID_COLOR_FEMME = "#FF69B4"
    PYRAMID_ANNOT_SEUIL = 0.18
    LOWER_WORDS = {"le", "la", "les", "de", "du", "des", "au", "aux"}
    HEATMAP_VMIN = 0
    HEATMAP_VMAX = 60

    def __init__(self, config: KarasekConfig = None):
        self.config = config or KarasekConfig()
        self.base_dir = Path(self.config.FIGURES_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ───────────────────────────────────────────────────────────────────────
    # HELPERS
    # ───────────────────────────────────────────────────────────────────────
    
    @staticmethod
    def _wrap(text: str, width: int) -> str:
        return "\n".join(textwrap.wrap(text, width=width))

    @staticmethod
    def _norm(text: str) -> str:
        return (unicodedata.normalize("NFD", str(text).lower().strip())
                .encode("ascii", "ignore").decode())

    @classmethod
    def _smart_capitalize(cls, text: str) -> str:
        words = text.split()
        result = []
        for i, w in enumerate(words):
            lw = w.lower()
            if i == 0:
                result.append(w.capitalize())
            elif lw in cls.LOWER_WORDS or lw.startswith("l'") or lw.startswith("d'"):
                result.append(lw)
            else:
                result.append(w.capitalize())
        return " ".join(result)

    def _get_palette(self, categories: List, col: str) -> Dict:
        n = self._norm(col)
        if "karasek" in n or "quadrant" in n:
            return {c: self.config.KARASEK_PALETTE.get(c, "#7f7f7f") for c in categories}
        if "strain" in n:
            return {c: self.config.STRAIN_PALETTE.get(c, "#7f7f7f") for c in categories}
        if "score" in n or any(c in self.config.SCORE_CAT_ORDER for c in categories):
            if col.startswith("Dem_") or "dem_" in col.lower():
                return {c: "#2ca02c" if c == "Faible" else "#d62728" for c in categories}
            return {c: "#2ca02c" if c == "Élevé" else "#d62728" for c in categories}
        colors = sns.color_palette("colorblind", len(categories))
        return dict(zip(categories, colors))

    def _save(self, folder: str, filename: str) -> str:
        d = self.base_dir / folder
        d.mkdir(parents=True, exist_ok=True)
        fp = d / filename
        plt.savefig(fp, dpi=300, bbox_inches="tight")
        plt.close()
        return str(fp)

    @staticmethod
    def _fname(col: str) -> str:
        return "".join(c if c.isalnum() or c in "_-" else "_" for c in col)[:80]

    def _label(self, col: str) -> str:
        return self.config.VAR_LABELS.get(col, col)

    # ───────────────────────────────────────────────────────────────────────
    # BARPLOT SIMPLE
    # ───────────────────────────────────────────────────────────────────────
    
    def plot_categorical(self, df: pd.DataFrame, col: str) -> Optional[str]:
        if col not in df.columns:
            return None
        data = df[col].dropna()
        if data.empty:
            return None

        mods = _sort_modalities(data, col, self.config.MODALITY_ORDER)
        counts = data.value_counts().reindex(mods).fillna(0).astype(int)
        pcts = (counts / counts.sum() * 100).round(1)
        colors = [self._get_palette(mods, col).get(m, "#7f7f7f") for m in mods]

        fig_h = max(4, len(mods) * 0.65 + 1.5)
        fig, ax = plt.subplots(figsize=(9, fig_h), constrained_layout=True)

        bars = ax.barh(mods, pcts, color=colors, edgecolor="white", height=0.6)

        for bar, pct, n in zip(bars, pcts, counts):
            if pct > 0:
                ax.text(
                    bar.get_width() + 0.8,
                    bar.get_y() + bar.get_height() / 2,
                    f"{pct}%  ({n})",
                    va="center", ha="left",
                    fontsize=self.ANNOT_SIZE,
                    fontweight="bold",
                )

        ax.set_xlim(0, 120)
        col_label = self._smart_capitalize(self._label(col))

        ax.set_title(
            self._wrap(f"Répartition des employés de {self.config.COMPANY_NAME} selon {col_label}",
                    self.TITLE_WRAP),
            fontsize=self.TITLE_SIZE, pad=14,
        )
        ax.set_xlabel("Pourcentage (%)", fontsize=self.LABEL_SIZE)
        ax.set_ylabel(self._wrap(col_label, self.YLABEL_WRAP),
                    fontsize=self.LABEL_SIZE, labelpad=10)
        ax.tick_params(axis="both", labelsize=self.TICK_SIZE)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        return self._save("sociodem", f"{self._fname(col)}_barplot.png")

    # ───────────────────────────────────────────────────────────────────────
    # STACKED BAR
    # ───────────────────────────────────────────────────────────────────────
    
    def plot_stacked_bar(self, df: pd.DataFrame, x_col: str, hue_col: str) -> Optional[str]:
        if x_col not in df.columns or hue_col not in df.columns:
            return None
        data = df[[x_col, hue_col]].dropna()
        if data.empty:
            return None

        x_order = _sort_modalities(data[x_col], x_col, self.config.MODALITY_ORDER)
        hue_order = _sort_modalities(data[hue_col], hue_col, self.config.MODALITY_ORDER)

        ct = pd.crosstab(data[x_col], data[hue_col])
        ct = ct.reindex(index=x_order, columns=hue_order, fill_value=0)
        pct = ct.div(ct.sum(axis=1), axis=0) * 100

        palette = self._get_palette(hue_order, hue_col)
        colors = [palette.get(m, "#7f7f7f") for m in hue_order]

        fig_h = max(4, len(x_order) * 0.8 + 2.5)
        fig, ax = plt.subplots(figsize=(13, fig_h))

        left = np.zeros(len(x_order))

        for i, hv in enumerate(hue_order):
            widths = pct[hv].values
            counts = ct[hv].values

            bars = ax.barh(
                x_order, widths, left=left,
                color=colors[i], edgecolor="white",
                label=self._smart_capitalize(str(hv)),
                height=0.65,
            )

            for bar, w, n in zip(bars, widths, counts):
                if w > 0:
                    x_c = bar.get_x() + bar.get_width() / 2
                    y_c = bar.get_y() + bar.get_height() / 2
                    if w < 6:
                        ax.text(
                            bar.get_x() + bar.get_width() + 0.5, y_c,
                            f"{w:.1f}%\n({n})",
                            ha="left", va="center",
                            fontsize=self.STACKED_ANNOT_SIZE,
                            fontweight=self.STACKED_ANNOT_WEIGHT,
                            color="#333333",
                        )
                    else:
                        ax.text(
                            x_c, y_c,
                            f"{w:.1f}%\n({n})",
                            ha="center", va="center",
                            fontsize=self.STACKED_ANNOT_SIZE,
                            fontweight=self.STACKED_ANNOT_WEIGHT,
                            color=self.STACKED_ANNOT_COLOR,
                        )
            left += widths

        x_label = self._smart_capitalize(self._label(x_col))
        hue_label = self._smart_capitalize(self._label(hue_col))

        ax.set_xlim(0, 100)
        ax.set_title(
            self._wrap(
                f"Répartition des employés de {self.config.COMPANY_NAME} selon {x_label} et {hue_label}",
                self.TITLE_WRAP),
            fontsize=self.TITLE_SIZE, pad=14,
        )
        ax.set_xlabel("Pourcentage (%)", fontsize=self.LABEL_SIZE)
        ax.set_ylabel(self._wrap(x_label, self.YLABEL_WRAP),
                    fontsize=self.LABEL_SIZE, labelpad=10)
        ax.tick_params(axis="both", labelsize=self.TICK_SIZE)

        legend = ax.legend(
            title=hue_label,
            fontsize=self.LEGEND_SIZE,
            title_fontsize=self.LEGEND_SIZE,
            bbox_to_anchor=(self.LEGEND_PAD, 1),
            loc="upper left",
            frameon=True,
        )
        legend.get_title().set_fontweight("bold")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.subplots_adjust(right=self.RIGHT_MARGIN, top=0.88, bottom=0.10, left=0.18)

        fname = f"{self._fname(hue_col)}_by_{self._fname(x_col)}.png"
        return self._save("stacked", fname)

    # ───────────────────────────────────────────────────────────────────────
    # SCATTERPLOT KARASEK (SEUIL THÉORIQUE UNIQUEMENT)
    # ───────────────────────────────────────────────────────────────────────
    
    def plot_karasek_scatter(self, df: pd.DataFrame) -> Optional[str]:
        """
        Scatterplot Karasek avec seuils THÉORIQUES uniquement.
        """
        quad_col = "Karasek_quadrant"
        required = ["Dem_score", "Lat_score", quad_col]
        missing = [c for c in required if c not in df.columns]
        if missing:
            logger.warning(f"Colonnes manquantes pour scatter : {missing}")
            return None

        data = df[required].dropna()
        if data.empty:
            return None

        dem_line = self.config.THRESHOLDS.get("Dem_score", 22.5)
        lat_line = self.config.THRESHOLDS.get("Lat_score", 60.0)

        QUAD_PALETTE = self.config.KARASEK_PALETTE
        QUAD_ORDER = ["Actif", "Detendu", "Tendu", "Passif"]
        present_quads = [q for q in QUAD_ORDER if q in data[quad_col].unique()]

        x_min, x_max = data["Dem_score"].min(), data["Dem_score"].max()
        y_min, y_max = data["Lat_score"].min(), data["Lat_score"].max()
        mx = (x_max - x_min) * 0.05
        my = (y_max - y_min) * 0.05
        x_lo, x_hi = x_min - mx, x_max + mx
        y_lo, y_hi = y_min - my, y_max + my

        fig, ax = plt.subplots(figsize=(10, 8))

        za = 0.06
        ax.fill_between([dem_line, x_hi], lat_line, y_hi, color=QUAD_PALETTE.get("Actif", "#22C55E"), alpha=za)
        ax.fill_between([x_lo, dem_line], lat_line, y_hi, color=QUAD_PALETTE.get("Detendu", "#38A3E8"), alpha=za)
        ax.fill_between([dem_line, x_hi], y_lo, lat_line, color=QUAD_PALETTE.get("Tendu", "#EF4444"), alpha=za)
        ax.fill_between([x_lo, dem_line], y_lo, lat_line, color=QUAD_PALETTE.get("Passif", "#94A3B8"), alpha=za)

        ax.axvline(dem_line, color="black", linestyle="--", linewidth=1.2)
        ax.axhline(lat_line, color="black", linestyle=":", linewidth=1.2)

        for quad in present_quads:
            subset = data[data[quad_col] == quad]
            n = len(subset)
            pct = n / len(data) * 100
            ax.scatter(
                subset["Dem_score"], subset["Lat_score"],
                c=QUAD_PALETTE.get(quad, "#7f7f7f"),
                label=f"{quad} ({pct:.1f}%)",
                s=60, alpha=0.75,
                edgecolors="white", linewidths=0.4,
            )

        for quad, (qx, qy, ha, va) in {
            "Actif":   (x_hi - mx * 0.5, y_hi - my * 0.5, "right", "top"),
            "Detendu": (x_lo + mx * 0.5, y_hi - my * 0.5, "left", "top"),
            "Tendu":   (x_hi - mx * 0.5, y_lo + my * 0.5, "right", "bottom"),
            "Passif":  (x_lo + mx * 0.5, y_lo + my * 0.5, "left", "bottom"),
        }.items():
            if quad in present_quads:
                ax.text(qx, qy, quad.upper(),
                        color=QUAD_PALETTE.get(quad, "#7f7f7f"),
                        fontsize=9, fontweight="bold",
                        ha=ha, va=va, alpha=0.55, zorder=5)

        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)

        ax.set_title(
            self._wrap(
                f"Répartition des employés de {self.config.COMPANY_NAME} — "
                f"Demande Psychologique × Latitude Décisionnelle\n(Seuil théorique)",
                self.TITLE_WRAP),
            fontsize=self.TITLE_SIZE, pad=14,
        )
        ax.set_xlabel("Demande Psychologique", fontsize=self.LABEL_SIZE)
        ax.set_ylabel(self._wrap("Latitude Décisionnelle", self.YLABEL_WRAP),
                    fontsize=self.LABEL_SIZE, labelpad=10)
        ax.tick_params(axis="both", labelsize=self.TICK_SIZE)

        legend = ax.legend(
            title="Quadrant de Karasek",
            bbox_to_anchor=(self.LEGEND_PAD, 1),
            loc="upper left",
            fontsize=self.LEGEND_SIZE,
            title_fontsize=self.LEGEND_SIZE,
            frameon=True,
        )
        legend.get_title().set_fontweight("bold")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.subplots_adjust(right=self.RIGHT_MARGIN, top=0.88, bottom=0.10, left=0.12)
        return self._save("scatter", "karasek_scatter_theoretical.png")

    # ───────────────────────────────────────────────────────────────────────
    # PYRAMIDE DES ÂGES
    # ───────────────────────────────────────────────────────────────────────
    
    def plot_age_pyramid(self, df: pd.DataFrame) -> Optional[str]:
        if "Tranche_age" not in df.columns or "Genre" not in df.columns:
            return None
        data = df[["Tranche_age", "Genre"]].dropna()
        if data.empty:
            return None

        age_order = _sort_modalities(data["Tranche_age"], "Tranche_age", self.config.MODALITY_ORDER)
        ct = pd.crosstab(data["Tranche_age"], data["Genre"]).reindex(age_order, fill_value=0)
        totaux = ct.sum(axis=0)
        ct_pct = ct.div(totaux, axis=1) * 100

        fig, ax = plt.subplots(figsize=(9, 7))

        homme_vals = ct_pct.get("Homme", pd.Series(0, index=age_order))
        femme_vals = ct_pct.get("Femme", pd.Series(0, index=age_order))
        homme_n = ct.get("Homme", pd.Series(0, index=age_order))
        femme_n = ct.get("Femme", pd.Series(0, index=age_order))

        max_val = max(homme_vals.max(), femme_vals.max()) * 1.15
        seuil = max_val * self.PYRAMID_ANNOT_SEUIL

        bars_h = ax.barh(age_order, -homme_vals, label="Homme", color=self.PYRAMID_COLOR_HOMME)
        bars_f = ax.barh(age_order, femme_vals, label="Femme", color=self.PYRAMID_COLOR_FEMME)

        def _annotate(bars, vals, ns, side: str):
            for bar, pct, n in zip(bars, vals, ns):
                if pct <= 0:
                    continue
                bar_w = abs(bar.get_width())
                y_c = bar.get_y() + bar.get_height() / 2
                label = f"{pct:.1f}%\n({n})"
                inside = bar_w >= seuil

                if inside:
                    x_pos = bar.get_x() + bar.get_width() / 2
                    ax.text(x_pos, y_c, label, ha="center", va="center",
                            fontsize=self.ANNOT_SIZE, fontweight="bold", color="white")
                else:
                    if side == "left":
                        x_pos = bar.get_x() - 0.5
                        ha = "right"
                    else:
                        x_pos = bar.get_x() + bar.get_width() + 0.5
                        ha = "left"
                    ax.text(x_pos, y_c, label, ha=ha, va="center",
                            fontsize=self.ANNOT_SIZE, fontweight="bold", color="#333333")

        _annotate(bars_h, homme_vals, homme_n, side="left")
        _annotate(bars_f, femme_vals, femme_n, side="right")

        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlim(-max_val, max_val)
        ticks = ax.get_xticks()
        ax.set_xticklabels([f"{abs(t):.0f}%" for t in ticks], fontsize=self.TICK_SIZE)

        ax.set_title(
            self._wrap(f"Répartition des employés de {self.config.COMPANY_NAME} "
                    "selon la Tranche d'âge et le Genre", self.TITLE_WRAP),
            fontsize=self.TITLE_SIZE, pad=14,
        )
        ax.set_xlabel("Pourcentage (%) au sein de chaque genre", fontsize=self.LABEL_SIZE)
        ax.set_ylabel(self._wrap("Tranche d'âge", self.YLABEL_WRAP),
                    fontsize=self.LABEL_SIZE, labelpad=10)
        ax.tick_params(axis="y", labelsize=self.TICK_SIZE)

        legend = ax.legend(bbox_to_anchor=(self.LEGEND_PAD, 1), loc="upper left",
                        fontsize=self.LEGEND_SIZE, frameon=True)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.subplots_adjust(right=self.RIGHT_MARGIN, top=0.88, bottom=0.12, left=0.18)
        return self._save("sociodem", "age_pyramid.png")

    # ───────────────────────────────────────────────────────────────────────
    # HEATMAP KARASEK PAR DIRECTION
    # ───────────────────────────────────────────────────────────────────────
    
    def plot_karasek_direction_heatmap(self, df: pd.DataFrame, group_col: str = "Direction") -> Optional[str]:
        """
        Heatmap des quadrants Karasek par Direction.
        Utilise les seuils THÉORIQUES.
        """
        quad_col = "Karasek_quadrant"
        if quad_col not in df.columns or group_col not in df.columns:
            return None

        ct = pd.crosstab(df[group_col], df[quad_col], normalize='index') * 100
        quadrants = ["Tendu", "Actif", "Passif", "Detendu"]
        for q in quadrants:
            if q not in ct.columns:
                ct[q] = 0

        ct = ct.sort_values("Tendu", ascending=True)

        colors_map = {
            "Tendu":   ["#ffffff", "#e74c3c"],
            "Actif":   ["#ffffff", "#3498db"],
            "Passif":  ["#ffffff", "#f39c12"],
            "Detendu": ["#ffffff", "#2ecc71"]
        }

        fig, axes = plt.subplots(1, 4, figsize=(20, 1 + len(ct)*0.4), sharey=True)
        fig.patch.set_facecolor("#f8f9fa")

        for ax, quad in zip(axes, quadrants):
            cmap = LinearSegmentedColormap.from_list(f"cmap_{quad}", colors_map[quad])
            sns.heatmap(
                ct[[quad]], ax=ax, cmap=cmap, vmin=self.HEATMAP_VMIN, vmax=self.HEATMAP_VMAX,
                annot=True, fmt=".0f", annot_kws={"size": 8},
                linewidths=0.5, linecolor="#eee", cbar=False
            )
            ax.set_title(quad.upper(), fontsize=11, fontweight="bold", color=colors_map[quad][1])
            ax.set_xlabel("%", fontsize=9)
            ax.tick_params(axis='y', labelsize=9)
            for spine in ax.spines.values():
                spine.set_visible(False)

        plt.suptitle(
            self._wrap(
                f"Répartition Karasek par {group_col} — seuil théorique "
                "(trié par tension décroissante)", 80),
            fontsize=self.TITLE_SIZE, fontweight="bold", y=1.02)

        return self._save("heatmaps", f"karasek_heatmap_by_{group_col}.png")

    # ───────────────────────────────────────────────────────────────────────
    # ORCHESTRATEUR GLOBAL
    # ───────────────────────────────────────────────────────────────────────
    
    def generate_all_plots(self, df: pd.DataFrame) -> Dict[str, str]:
        results = {}

        print("=====Graphiques socio-démographiques=====")
        for col in self.config.CAT_VARS:
            p = self.plot_categorical(df, col)
            if p:
                results[f"cat_{col}"] = p

        p = self.plot_age_pyramid(df)
        if p:
            results["age_pyramid"] = p

        print("=====Graphiques croisés=====")
        for x_col, hue_col in self.config.ALL_CROSSTABS:
            p = self.plot_stacked_bar(df, x_col, hue_col)
            if p:
                results[f"stacked_{hue_col}_by_{x_col}"] = p

        print("=====Scatterplot Karasek (seuil théorique)=====")
        p = self.plot_karasek_scatter(df)
        if p:
            results["scatter_theoretical"] = p

        print("=====Heatmap organisationnelle=====")
        p = self.plot_karasek_direction_heatmap(df, group_col="Direction")
        if p:
            results["heatmap_karasek"] = p

        print(f"{len(results)} graphiques générés au total")
        return results