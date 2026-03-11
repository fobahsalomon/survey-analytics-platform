# -*- coding: utf-8 -*-
"""
reporting.py — Export du module Karasek
UNIQUEMENT de l'export : Excel, figures, Word.
Aucune logique statistique ici.
"""

import logging
import os
import textwrap
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils.dataframe import dataframe_to_rows

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import config as cfg

logger = logging.getLogger(__name__)

# ===========================================================================
# CONSTANTES GRAPHIQUES (ajustables sans toucher à la logique)
# ===========================================================================
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

SCORE_CAT_PALETTE     = {"Faible": "#d62728", "Moyen": "#ff7f0e", "Élevé": "#2ca02c"}
INV_SCORE_CAT_PALETTE = {"Faible": "#2ca02c", "Moyen": "#ff7f0e", "Élevé": "#d62728"}
MUTED       = "#7f7f7f"
LOWER_WORDS = {"le", "la", "les", "de", "du", "des", "au", "aux"}


# ===========================================================================
# HELPERS GRAPHIQUES INTERNES
# ===========================================================================

def _wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def _smart_capitalize(text: str) -> str:
    words, result = text.split(), []
    for i, w in enumerate(words):
        lw = w.lower()
        if i == 0 or (lw not in LOWER_WORDS
                    and not lw.startswith("l'")
                    and not lw.startswith("d'")):
            result.append(w.capitalize())
        else:
            result.append(lw)
    return " ".join(result)


def _norm(text: str) -> str:
    return (unicodedata.normalize("NFD", str(text).lower().strip())
            .encode("ascii", "ignore").decode())


def _get_palette(categories: List, col: str) -> Dict:
    n = _norm(col)
    if "karasek" in n or "quadrant" in n:
        return {c: cfg.KARASEK_PALETTE.get(c, MUTED) for c in categories}
    if "strain" in n:
        return {c: cfg.STRAIN_PALETTE.get(c, MUTED) for c in categories}
    if "score" in n or any(c in cfg.SCORE_CAT_ORDER for c in categories):
        if col.startswith("Dem_") or "dem_" in col.lower():
            return {c: INV_SCORE_CAT_PALETTE.get(c, MUTED) for c in categories}
        return {c: SCORE_CAT_PALETTE.get(c, MUTED) for c in categories}
    colors = sns.color_palette("colorblind", len(categories))
    return dict(zip(categories, colors))


def _sort_modalities(series: pd.Series, col_name: str) -> List:
    present = list(series.dropna().unique())
    if col_name in cfg.MODALITY_ORDER:
        ordered  = [m for m in cfg.MODALITY_ORDER[col_name] if m in present]
        ordered += [m for m in present if m not in ordered]
        return ordered
    if set(cfg.SCORE_CAT_ORDER).intersection(present):
        ordered  = [m for m in cfg.SCORE_CAT_ORDER if m in present]
        ordered += [m for m in present if m not in ordered]
        return ordered
    return sorted(present, key=str)


def _fname(col: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in col)[:80]


def _label(col: str) -> str:
    return cfg.VAR_LABELS.get(col, col)


def _title(company: str, suffix: str) -> str:
    return f"Répartition des employés de {company} selon {suffix}"


def _save_fig(fig: plt.Figure, folder: Path, filename: str) -> str:
    folder.mkdir(parents=True, exist_ok=True)
    fp = folder / filename
    fig.savefig(fp, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return str(fp)


# ===========================================================================
# FIGURES INTERNES
# ===========================================================================

def _plot_categorical(df: pd.DataFrame, col: str,
                    company: str, out_dir: Path) -> Optional[str]:
    if col not in df.columns:
        return None
    data = df[col].dropna()
    if data.empty:
        return None

    mods   = _sort_modalities(data, col)
    counts = data.value_counts().reindex(mods).fillna(0).astype(int)
    pcts   = (counts / counts.sum() * 100).round(1)
    colors = [_get_palette(mods, col).get(m, MUTED) for m in mods]

    fig_h = max(4, len(mods) * 0.65 + 1.5)
    fig, ax = plt.subplots(figsize=(9, fig_h), constrained_layout=True)
    bars = ax.barh(mods, pcts, color=colors, edgecolor="white", height=0.6)

    for bar, pct, n in zip(bars, pcts, counts):
        if pct > 0:
            ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                    f"{pct}%  ({n})", va="center", ha="left",
                    fontsize=ANNOT_SIZE, fontweight="bold")

    col_label = _smart_capitalize(_label(col))
    ax.set_xlim(0, 120)
    ax.set_title(_wrap(_title(company, col_label), TITLE_WRAP),
                fontsize=TITLE_SIZE, pad=14)
    ax.set_xlabel("Pourcentage (%)", fontsize=LABEL_SIZE)
    ax.set_ylabel(_wrap(col_label, YLABEL_WRAP), fontsize=LABEL_SIZE, labelpad=10)
    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return _save_fig(fig, out_dir / "distributions", f"{_fname(col)}_barplot.png")


def _plot_stacked_bar(df: pd.DataFrame, x_col: str, hue_col: str,
                    company: str, out_dir: Path) -> Optional[str]:
    if x_col not in df.columns or hue_col not in df.columns:
        return None
    data = df[[x_col, hue_col]].dropna()
    if data.empty:
        return None

    x_order   = _sort_modalities(data[x_col],   x_col)
    hue_order = _sort_modalities(data[hue_col], hue_col)
    ct  = pd.crosstab(data[x_col], data[hue_col])
    ct  = ct.reindex(index=x_order, columns=hue_order, fill_value=0)
    pct = ct.div(ct.sum(axis=1), axis=0) * 100

    palette = _get_palette(hue_order, hue_col)
    colors  = [palette.get(m, MUTED) for m in hue_order]

    fig_h = max(4, len(x_order) * 0.8 + 2.5)
    fig, ax = plt.subplots(figsize=(13, fig_h))
    left = np.zeros(len(x_order))

    for i, hv in enumerate(hue_order):
        widths = pct[hv].values
        counts = ct[hv].values
        bars = ax.barh(x_order, widths, left=left, color=colors[i],
                    edgecolor="white",
                    label=_smart_capitalize(str(hv)), height=0.65)

        for bar, w, n in zip(bars, widths, counts):
            if w > 0:
                x_c = bar.get_x() + bar.get_width() / 2
                y_c = bar.get_y() + bar.get_height() / 2
                if w < 6:
                    ax.text(bar.get_x() + bar.get_width() + 0.5, y_c,
                            f"{w:.1f}%\n({n})", ha="left", va="center",
                            fontsize=STACKED_ANNOT_SIZE,
                            fontweight=STACKED_ANNOT_WEIGHT, color="#333333")
                else:
                    ax.text(x_c, y_c, f"{w:.1f}%\n({n})",
                            ha="center", va="center",
                            fontsize=STACKED_ANNOT_SIZE,
                            fontweight=STACKED_ANNOT_WEIGHT, color=STACKED_ANNOT_COLOR)
        left += widths

    x_label   = _smart_capitalize(_label(x_col))
    hue_label = _smart_capitalize(_label(hue_col))

    ax.set_xlim(0, 100)
    ax.set_title(_wrap(_title(company, f"{x_label} et {hue_label}"), TITLE_WRAP),
                fontsize=TITLE_SIZE, pad=14)
    ax.set_xlabel("Pourcentage (%)", fontsize=LABEL_SIZE)
    ax.set_ylabel(_wrap(x_label, YLABEL_WRAP), fontsize=LABEL_SIZE, labelpad=10)
    ax.tick_params(axis="both", labelsize=TICK_SIZE)

    legend = ax.legend(title=hue_label, fontsize=LEGEND_SIZE,
                    title_fontsize=LEGEND_SIZE,
                    bbox_to_anchor=(LEGEND_PAD, 1), loc="upper left", frameon=True)
    legend.get_title().set_fontweight("bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.subplots_adjust(right=RIGHT_MARGIN, top=0.88, bottom=0.10, left=0.18)

    return _save_fig(fig, out_dir / "crosstabs",
                    f"{_fname(hue_col)}_by_{_fname(x_col)}.png")


def _plot_karasek_scatter(df: pd.DataFrame, company: str,
                        out_dir: Path) -> Optional[str]:
    required = ["Dem_score", "Lat_score", "Karasek_quadrant_internal"]
    if any(c not in df.columns for c in required):
        return None
    data = df[required].dropna()
    if data.empty:
        return None

    dem_med = data["Dem_score"].median()
    lat_med = data["Lat_score"].median()
    QUAD_ORDER = ["Actif", "Detendu", "Tendu", "Passif"]
    present    = [q for q in QUAD_ORDER
                if q in data["Karasek_quadrant_internal"].unique()]

    x_min, x_max = data["Dem_score"].min(), data["Dem_score"].max()
    y_min, y_max = data["Lat_score"].min(), data["Lat_score"].max()
    mx = (x_max - x_min) * 0.05
    my = (y_max - y_min) * 0.05
    x_lo, x_hi = x_min - mx, x_max + mx
    y_lo, y_hi = y_min - my, y_max + my

    fig, ax = plt.subplots(figsize=(10, 8))
    za = 0.06
    ax.fill_between([dem_med, x_hi], lat_med, y_hi,
                    color=cfg.KARASEK_PALETTE["Actif"],   alpha=za)
    ax.fill_between([x_lo, dem_med], lat_med, y_hi,
                    color=cfg.KARASEK_PALETTE["Detendu"], alpha=za)
    ax.fill_between([dem_med, x_hi], y_lo, lat_med,
                    color=cfg.KARASEK_PALETTE["Tendu"],   alpha=za)
    ax.fill_between([x_lo, dem_med], y_lo, lat_med,
                    color=cfg.KARASEK_PALETTE["Passif"],  alpha=za)
    ax.axvline(dem_med, color="black", linestyle="--", linewidth=1.2)
    ax.axhline(lat_med, color="black", linestyle=":",  linewidth=1.2)

    for quad in present:
        sub = data[data["Karasek_quadrant_internal"] == quad]
        pct = len(sub) / len(data) * 100
        ax.scatter(sub["Dem_score"], sub["Lat_score"],
                c=cfg.KARASEK_PALETTE[quad],
                label=f"{quad} ({pct:.1f}%)",
                s=60, alpha=0.75, edgecolors="white", linewidths=0.4)

    corners = {
        "Actif":   (x_hi - mx * 0.5, y_hi - my * 0.5, "right", "top"),
        "Detendu": (x_lo + mx * 0.5, y_hi - my * 0.5, "left",  "top"),
        "Tendu":   (x_hi - mx * 0.5, y_lo + my * 0.5, "right", "bottom"),
        "Passif":  (x_lo + mx * 0.5, y_lo + my * 0.5, "left",  "bottom"),
    }
    for quad, (qx, qy, ha, va) in corners.items():
        if quad in present:
            ax.text(qx, qy, quad.upper(), color=cfg.KARASEK_PALETTE[quad],
                    fontsize=9, fontweight="bold", ha=ha, va=va, alpha=0.55, zorder=5)

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)
    ax.set_title(
        _wrap(f"Répartition des employés de {company} — "
            "Demande Psychologique × Latitude Décisionnelle", TITLE_WRAP),
        fontsize=TITLE_SIZE, pad=14)
    ax.set_xlabel("Demande Psychologique", fontsize=LABEL_SIZE)
    ax.set_ylabel(_wrap("Latitude Décisionnelle", YLABEL_WRAP),
                fontsize=LABEL_SIZE, labelpad=10)
    ax.tick_params(axis="both", labelsize=TICK_SIZE)
    legend = ax.legend(title="Quadrant de Karasek",
                    bbox_to_anchor=(LEGEND_PAD, 1), loc="upper left",
                    fontsize=LEGEND_SIZE, title_fontsize=LEGEND_SIZE, frameon=True)
    legend.get_title().set_fontweight("bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.subplots_adjust(right=RIGHT_MARGIN, top=0.88, bottom=0.10, left=0.12)

    return _save_fig(fig, out_dir / "scales", "karasek_scatter.png")


def _plot_age_pyramid(df: pd.DataFrame, company: str,
                    out_dir: Path) -> Optional[str]:
    if "Tranche_age" not in df.columns or "Genre" not in df.columns:
        return None
    data = df[["Tranche_age", "Genre"]].dropna()
    if data.empty:
        return None

    age_order = _sort_modalities(data["Tranche_age"], "Tranche_age")
    ct     = pd.crosstab(data["Tranche_age"], data["Genre"]).reindex(age_order, fill_value=0)
    ct_pct = ct.div(ct.sum(axis=0), axis=1) * 100

    homme_vals = ct_pct.get("Homme", pd.Series(0, index=age_order))
    femme_vals = ct_pct.get("Femme", pd.Series(0, index=age_order))
    homme_n    = ct.get("Homme",    pd.Series(0, index=age_order))
    femme_n    = ct.get("Femme",    pd.Series(0, index=age_order))

    max_val = max(homme_vals.max(), femme_vals.max()) * 1.15
    seuil   = max_val * PYRAMID_ANNOT_SEUIL

    fig, ax = plt.subplots(figsize=(9, 7))
    bars_h = ax.barh(age_order, -homme_vals, label="Homme",
                    color=PYRAMID_COLOR_HOMME)
    bars_f = ax.barh(age_order,  femme_vals, label="Femme",
                    color=PYRAMID_COLOR_FEMME)

    def _annotate(bars, vals, ns, side):
        for bar, pct, n in zip(bars, vals, ns):
            if pct <= 0:
                continue
            y_c   = bar.get_y() + bar.get_height() / 2
            label = f"{pct:.1f}%\n({n})"
            if abs(bar.get_width()) >= seuil:
                ax.text(bar.get_x() + bar.get_width() / 2, y_c, label,
                        ha="center", va="center",
                        fontsize=ANNOT_SIZE, fontweight="bold", color="white")
            else:
                x_pos = bar.get_x() - 0.5 if side == "left" else \
                        bar.get_x() + bar.get_width() + 0.5
                ha    = "right" if side == "left" else "left"
                ax.text(x_pos, y_c, label, ha=ha, va="center",
                        fontsize=ANNOT_SIZE, fontweight="bold", color="#333333")

    _annotate(bars_h, homme_vals, homme_n, "left")
    _annotate(bars_f, femme_vals, femme_n, "right")

    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlim(-max_val, max_val)
    ax.set_xticklabels([f"{abs(t):.0f}%" for t in ax.get_xticks()],
                    fontsize=TICK_SIZE)
    ax.set_title(
        _wrap(f"Répartition des employés de {company} "
            "selon la Tranche d'âge et le Genre", TITLE_WRAP),
        fontsize=TITLE_SIZE, pad=14)
    ax.set_xlabel("Pourcentage (%) au sein de chaque genre", fontsize=LABEL_SIZE)
    ax.set_ylabel(_wrap("Tranche d'âge", YLABEL_WRAP),
                fontsize=LABEL_SIZE, labelpad=10)
    ax.tick_params(axis="y", labelsize=TICK_SIZE)
    ax.legend(bbox_to_anchor=(LEGEND_PAD, 1), loc="upper left",
            fontsize=LEGEND_SIZE, frameon=True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.subplots_adjust(right=RIGHT_MARGIN, top=0.88, bottom=0.12, left=0.18)

    return _save_fig(fig, out_dir / "distributions", "age_pyramid.png")

# ===========================================================================
# EXPORT EXCEL
# ===========================================================================

def _make_sheet_name(rv: str, col_var: str, existing: set) -> str:
    """Génère un nom d'onglet unique ≤ 31 caractères."""
    # Abréviations courantes pour gagner de la place
    abbrevs = {
        "Karasek_quadrant_internal": "Karasek_Q",
        "Iso_strain_internal":       "Iso_strain",
        "Job_strain_internal":       "Job_strain",
        "Tranche_anciennete":        "Tr_anciennete",
        "Tranche_age":               "Tr_age",
        "Categorie_IMC":             "Cat_IMC",
        "Avez-vous une maladie chronique": "Maladie_chr",
        "Pratique reguliere du sport":     "Sport",
        "Catégorie Socio":           "Cat_Socio",
        "sat_score_quant_cat":       "sat",
        "cult_score_quant_cat":      "cult",
        "equ_score_quant_cat":       "equ",
        "SS_score_quant_cat":        "SS",
        "col_score_quant_cat":       "col",
        "sup_score_quant_cat":       "sup",
        "rec_score_quant_cat":       "rec",
        "adq_resources_score_quant_cat": "adq_res",
        "adq_role_score_quant_cat":  "adq_role",
    }
    rv_short  = abbrevs.get(rv,  rv)
    cv_short  = abbrevs.get(col_var, col_var)
    name = f"{rv_short} × {cv_short}"

    # Tronquer si encore trop long
    if len(name) > 31:
        name = name[:31]

    # Garantir l'unicité
    base, i = name, 1
    while name in existing:
        suffix = f"_{i}"
        name = base[:31 - len(suffix)] + suffix
        i += 1

    existing.add(name)
    return name

def export_excel(questionnaire, output_path: str) -> None:
    """
    Génère karasek_results.xlsx avec les onglets :
    - raw_descriptives
    - prevalences
    - un onglet par paire de variables croisées (% ligne + % colonne)
    """
    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, "karasek_results.xlsx")


    def thin_border():
        return Border(**{s: Side(style="thin") for s in ("left", "right", "top", "bottom")})

    header_fill = PatternFill("solid", fgColor="2E75B6")
    header_font = Font(bold=True, color="FFFFFF")

    def _auto_col_width(ws):
        for col in ws.columns:
            cell = col[0]
            if not hasattr(cell, "column_letter"):
                continue
            max_len = max((len(str(c.value or "")) for c in col), default=10)
            ws.column_dimensions[cell.column_letter].width = min(max_len + 4, 40)

    def _build_crosstab(df: pd.DataFrame, row_var: str, col_var: str,
                        by: str = "row", rd: int = 1) -> pd.DataFrame:
        tmp = df[[row_var, col_var]].dropna()
        ct  = pd.crosstab(tmp[row_var], tmp[col_var])

        row_totals  = ct.sum(axis=1)
        col_totals  = ct.sum(axis=0)
        grand_total = ct.sum().sum()

        if by == "row":
            ct_pct        = ct.div(row_totals, axis=0) * 100
            total_col_pct = pd.Series(100.0, index=ct.index)
            total_row_pct = (col_totals / grand_total * 100) if grand_total > 0 else pd.Series(0.0, index=col_totals.index)
        else:
            ct_pct        = ct.div(col_totals, axis=1) * 100
            total_row_pct = pd.Series(100.0, index=ct.columns)
            total_col_pct = (row_totals / grand_total * 100) if grand_total > 0 else pd.Series(0.0, index=row_totals.index)

        result = pd.DataFrame(index=ct.index, columns=ct.columns, dtype=object)
        for col in ct.columns:
            for idx in ct.index:
                n   = int(ct.at[idx, col])
                pct = ct_pct.at[idx, col]
                result.at[idx, col] = f"{n} ({pct:.{rd}f}%)"

        result["Total"] = [
            f"{int(row_totals[idx])} ({total_col_pct[idx]:.{rd}f}%)"
            for idx in ct.index
        ]
        total_row = {col: f"{int(col_totals[col])} ({total_row_pct[col]:.{rd}f}%)" for col in ct.columns}
        total_row["Total"] = f"{int(grand_total)} (100.0%)"
        result.loc["Total"] = pd.Series(total_row)

        return result

    def _style_ws(ws, df_in: pd.DataFrame, include_index: bool = True):
        for r_idx, row in enumerate(
            dataframe_to_rows(df_in, index=include_index, header=True), 1
        ):
            ws.append(row)
            for cell in ws[r_idx]:
                cell.border    = thin_border()
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if r_idx == 1:
                    cell.fill = header_fill
                    cell.font = header_font
        _auto_col_width(ws)

    wb = Workbook()
    wb.remove(wb.active)

    # --- Onglet raw_descriptives ---
    if questionnaire.descriptives is not None:
        ws = wb.create_sheet("raw_descriptives")
        _style_ws(ws, questionnaire.descriptives, include_index=False)

    # --- Onglet prevalences ---
    if questionnaire.prevalences is not None:
        ws = wb.create_sheet("prevalences")
        _style_ws(ws, questionnaire.prevalences, include_index=False)

    # --- Onglets tableaux croisés ---
    if questionnaire.crosstabs:
        df_source = pd.concat(
            [questionnaire.cleaned_df, questionnaire.scores_df], axis=1
        )
        df_source = df_source.loc[:, ~df_source.columns.duplicated()]
        
        existing_sheets = set()
        for rv, cv in cfg.ALL_CROSSTABS:
            if rv not in df_source.columns or cv not in df_source.columns:
                logger.info(f"Crosstab sauté (colonne absente) : {rv} × {cv}")
                continue

            sheet_name = _make_sheet_name(rv, cv, existing_sheets)
            ws = wb.create_sheet(sheet_name)
            
            # Titre général
            ws.append([f"Tableau croisé – {rv} × {cv}"])
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=10)
            ws["A1"].font      = Font(bold=True, size=13)
            ws["A1"].alignment = Alignment(horizontal="center")

            cur = 3
            for by, label in [("row", "% par ligne"), ("col", "% par colonne")]:
                tbl = _build_crosstab(df_source, rv, cv, by=by)

                # Titre sous-tableau
                title_cell = ws.cell(row=cur, column=1, value=f"{rv} × {cv}  ({label})")
                title_cell.font      = Font(bold=True, size=11)
                title_cell.alignment = Alignment(horizontal="left")
                cur += 1

                for r_idx, row in enumerate(
                    dataframe_to_rows(tbl, index=True, header=True), cur
                ):
                    ws.append(row)
                    for cell in ws[r_idx]:
                        cell.border    = thin_border()
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        if r_idx == cur:
                            cell.fill = header_fill
                            cell.font = header_font
                    cur += 1

                cur += 2  # espace entre les deux sous-tableaux

            _auto_col_width(ws)

    wb.save(file_path)
    print(f"   📊 Excel exporté → {file_path}")

# ===========================================================================
# EXPORT FIGURES
# ===========================================================================

def export_figures(questionnaire, output_path: str) -> None:
    """
    Génère toutes les figures dans output_path/figures/
    Sous-dossiers : distributions/, scales/, crosstabs/
    """
    out_dir = Path(output_path) / "figures"
    company = questionnaire.company_name
    df      = questionnaire.scores_df if questionnaire.scores_df is not None \
            else questionnaire.cleaned_df
    results = {}

    # Scatter Karasek
    p = _plot_karasek_scatter(df, company, out_dir)
    if p: results["karasek_scatter"] = p

    # Pyramide des âges
    p = _plot_age_pyramid(df, company, out_dir)
    if p: results["age_pyramid"] = p

    # Barplots simples
    score_cat_cols = [c for c in df.columns
                    if c.endswith("_quant_cat") or c.endswith("_internal")]
    all_cat = list(cfg.CAT_VARS) + [c for c in score_cat_cols
                                    if c not in cfg.CAT_VARS]
    for col in all_cat:
        if col not in df.columns:
            continue
        p = _plot_categorical(df, col, company, out_dir)
        if p: results[f"cat_{col}"] = p

    # Stacked bars (tableaux croisés)
    for x_col, hue_col in cfg.ALL_CROSSTABS:
        p = _plot_stacked_bar(df, x_col, hue_col, company, out_dir)
        if p: results[f"stacked_{x_col}_x_{hue_col}"] = p

    print(f"   🖼  {len(results)} graphiques exportés → {out_dir}")


# ===========================================================================
# EXPORT WORD
# ===========================================================================

def export_word(questionnaire, output_path: str) -> None:
    """
    Génère karasek_statistics.docx avec :
    1. Description de l'échantillon
    2. Statistiques descriptives
    3. Quadrants et prévalences Karasek
    4. Scores RH
    5. Tableaux croisés (résumé, 10 premiers)
    6. Conclusion factuelle
    """
    try:
        from docx import Document
        from docx.shared import Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("   ⚠️  python-docx non installé → export Word ignoré.")
        return

    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, "karasek_statistics.docx")

    doc     = Document()
    company = questionnaire.company_name
    df      = questionnaire.scores_df if questionnaire.scores_df is not None \
            else questionnaire.cleaned_df
    metrics = getattr(questionnaire, "metrics", {})

    # ── Helpers ───────────────────────────────────────────────────────
    def _h(text, level=1):
        doc.add_heading(text, level=level)

    def _p(text, bold=False):
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold

    def _add_table(df_in: pd.DataFrame):
        if df_in is None or df_in.empty:
            _p("(Aucune donnée disponible)")
            return
        cols = [df_in.index.name or ""] + list(df_in.columns)
        t = doc.add_table(rows=1, cols=len(cols))
        t.style = "Table Grid"
        for j, c in enumerate(cols):
            cell = t.rows[0].cells[j]
            cell.text = str(c)
            cell.paragraphs[0].runs[0].bold = True
        for idx, row in df_in.iterrows():
            cells = t.add_row().cells
            cells[0].text = str(idx)
            for j, val in enumerate(row, 1):
                cells[j].text = str(val) if val is not None else ""
        doc.add_paragraph()

    # ── Page de titre ─────────────────────────────────────────────────
    title_p = doc.add_heading(f"Analyse Karasek – {company}", 0)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _p(f"Date d'analyse : {datetime.now():%d/%m/%Y}")
    doc.add_page_break()

    # ── 1. Description de l'échantillon ──────────────────────────────
    _h("1. Description de l'échantillon")
    n_initial = metrics.get("rows_initial", "N/A")
    n_final   = metrics.get("rows_final",   len(df))
    _p(f"Effectif initial : {n_initial} répondants")
    _p(f"Effectif retenu  : {n_final} répondants")

    if "Genre" in df.columns:
        _p("Répartition par genre :", bold=True)
        for genre, n in df["Genre"].value_counts().items():
            _p(f"   • {genre} : {n} ({n/len(df)*100:.1f}%)")

    if "Tranche_age" in df.columns:
        _p("Répartition par tranche d'âge :", bold=True)
        for ta, n in df["Tranche_age"].value_counts().sort_index().items():
            _p(f"   • {ta} : {n} ({n/len(df)*100:.1f}%)")
    doc.add_page_break()

    # ── 2. Statistiques descriptives ──────────────────────────────────
    _h("2. Statistiques descriptives des scores")
    if questionnaire.descriptives is not None:
        _add_table(questionnaire.descriptives.set_index("Variable"))
    doc.add_page_break()

    # ── 3. Résultats Karasek ──────────────────────────────────────────
    _h("3. Résultats Karasek")
    thresholds = metrics.get("thresholds", df.attrs.get("thresholds", {}))
    if thresholds:
        _p("Seuils (médianes internes) :", bold=True)
        for k, v in thresholds.items():
            _p(f"   • {k} : {v:.2f}")

    _h("Répartition des quadrants", level=2)
    if "Karasek_quadrant" in df.columns:
        vc    = df["Karasek_quadrant"].value_counts()
        total = vc.sum()
        for quad in ["Actif", "Detendu", "Tendu", "Passif"]:
            n = vc.get(quad, 0)
            _p(f"   • {quad} : {n} ({n/total*100:.1f}%)")

    _h("Prévalence RPS", level=2)
    if questionnaire.prevalences is not None and not questionnaire.prevalences.empty:
        _add_table(questionnaire.prevalences.set_index("Indicateur"))
    doc.add_page_break()

    # ── 4. Scores RH ──────────────────────────────────────────────────
    _h("4. Scores RH")
    for g in cfg.RH_SCORE_GROUPS:
        sc  = f"{g}_score"
        cat = f"{sc}_quant_cat"
        if sc not in df.columns:
            continue
        lbl = cfg.SCORE_LABELS.get(sc, sc)
        s   = df[sc].dropna()
        _h(lbl, level=2)
        _p(f"Moyenne : {s.mean():.2f} ± {s.std():.2f}  |  Médiane : {s.median():.2f}")
        if cat in df.columns:
            vc = df[cat].value_counts()
            for m in ["Faible", "Moyen", "Élevé"]:
                n = vc.get(m, 0)
                _p(f"   • {m} : {n} ({n/len(df)*100:.1f}%)")
    doc.add_page_break()

    # ── 5. Tableaux croisés (résumé, 10 premiers) ─────────────────────
    _h("5. Tableaux croisés — résumé")
    if questionnaire.crosstabs:
        for key, tbl in list(questionnaire.crosstabs.items())[:10]:
            _h(key, level=2)
            _add_table(tbl)
    doc.add_page_break()

    # ── 6. Conclusion factuelle ───────────────────────────────────────
    _h("6. Conclusion factuelle")
    _p(
        "Ce document présente les résultats bruts de l'analyse Karasek. "
        "Les classifications sont réalisées par médianes internes à l'échantillon. "
        "Aucune interprétation subjective n'est portée dans ce rapport automatisé."
    )

    doc.save(file_path)
    print(f"   📄 Word exporté → {file_path}")
