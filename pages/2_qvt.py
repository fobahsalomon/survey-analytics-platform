"""
pages/2_qvt.py
Dashboard QVT — Qualité de Vie au Travail
Utilise lib/questionnaires/qvt comme engine backend.
"""

import sys
import re
import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import warnings

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# La page QVT suit la même architecture que les autres pages :
# upload -> pipeline -> filtres -> analytics -> visuels -> export.
from lib.questionnaires.qvt import QVTQuestionnaire, QVTReporting, QVTVisualizations
from lib.questionnaires.qvt.config import DIMENSIONS, THRESHOLDS, QVT_COLORS
from lib.common.file_utils import load_dataframe
from pages._export_utils import render_zip_button, build_zip
from pages._ui_shared import (
    inject_css, inject_animation_js,
    section_title, svg_icon, html_kpi, html_gauge_raw, html_prog,
    html_zone, html_ls_n, make_barplot, make_stacked, make_radar,
    _plotly_base, fig_to_png, render_sidebar, render_export_button,
    _norm,
)

st.set_page_config(
    page_title="QVT · SurveyLens",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
inject_animation_js()

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">',
    unsafe_allow_html=True,
)

# ─── TOPBAR ──────────────────────────────────────────────────────────────────
_col_top, _col_back = st.columns([9, 1])
with _col_top:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;background:white;border-radius:12px;'
        'padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),'
        '0 4px 12px rgba(34,197,94,0.08);border:1px solid #e8edf5;">'
        '<div style="width:38px;height:38px;background:linear-gradient(135deg,#15803D,#22C55E);'
        'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        '<i class="fas fa-leaf" style="color:white;font-size:15px;"></i></div>'
        '<div>'
        '<div style="font-size:16px;font-weight:700;color:#1e293b;">Qualité de Vie au Travail — QVT</div>'
        '<div style="font-size:11px;color:#64748b;margin-top:1px;">Analyse des 6 dimensions ANACT · Accord National Interprofessionnel 2013</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
with _col_back:
    if st.button("← Accueil", key="back_home_qvt", use_container_width=True):
        st.switch_page("app.py")

# ─── UPLOAD ──────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Charger un fichier Excel ou CSV",
    type=["xlsx", "xls", "csv"],
    key="qvt_uploader",
)
if uploaded is not None:
    st.session_state["_qvt_bytes"] = uploaded.read()
    st.session_state["_qvt_name"]  = uploaded.name

if "_qvt_bytes" not in st.session_state:
    st.info("Veuillez charger un fichier de données pour démarrer l'analyse QVT.")
    st.stop()

# ─── PIPELINE ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_pipeline(file_bytes: bytes, file_name: str, _v: int = 1):
    """Charge, nettoie, score et classe un fichier QVT."""
    # Le cache protège l'expérience utilisateur : changer un filtre ne doit pas
    # forcer la relecture complète du fichier.
    q  = QVTQuestionnaire()
    df = load_dataframe(io.BytesIO(file_bytes), file_name=file_name)
    return q.run(df)

with st.spinner("Traitement des données…"):
    df_scored = run_pipeline(st.session_state["_qvt_bytes"], st.session_state["_qvt_name"])

# ─── SIDEBAR FILTRES ─────────────────────────────────────────────────────────
df = render_sidebar(df_scored, prefix="qvt")

with st.sidebar:
    n_f = len(df)
    st.markdown(f"""<div style="text-align:center;padding:0.7rem;background:#DCFCE7;border-radius:10px;margin-top:0.8rem;">
    <span style="font-size:0.7rem;color:#15803D;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Effectif filtré</span><br>
    <span style="font-size:1.6rem;font-weight:800;color:#22C55E;">{n_f}</span>
    </div>""", unsafe_allow_html=True)

    # Export
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<span style="font-size:0.7rem;font-weight:700;color:#6B88A8;text-transform:uppercase;letter-spacing:0.08em;">Export</span>', unsafe_allow_html=True)
    company_qvt = st.text_input("Nom organisation", value="Mon Organisation", key="qvt_company")
    if st.button("Générer rapport + visuels", key="qvt_gen_report", use_container_width=True):
        with st.spinner("Génération des visualisations…"):
            try:
                viz_qvt = QVTVisualizations(company=company_qvt)
                q_engine_tmp = QVTQuestionnaire()
                metrics_tmp  = q_engine_tmp.analytics(df)
                figs_qvt = viz_qvt.generate_all(df, metrics_tmp)
                st.session_state["_qvt_figures"] = figs_qvt
            except Exception as e:
                st.warning(f"Visualisations partielles : {e}")
                st.session_state["_qvt_figures"] = {}
        with st.spinner("Génération du rapport Word…"):
            try:
                q_engine = QVTQuestionnaire()
                metrics  = q_engine.analytics(df)
                reporter = QVTReporting(company_name=company_qvt)
                docx_bytes = reporter.generate(
                    metrics,
                    figures=st.session_state.get("_qvt_figures", {}),
                )
                st.session_state["_qvt_report"] = docx_bytes
                n_figs = len(st.session_state.get("_qvt_figures", {}))
                st.success(f"Rapport prêt — {n_figs} figure(s) incluse(s)")
            except ImportError as e:
                st.error(f"python-docx manquant : {e}")
            except Exception as e:
                st.error(f"Erreur rapport : {e}")
    if "_qvt_report" in st.session_state:
        render_export_button(st.session_state["_qvt_report"], "rapport_qvt.docx")
    if "_qvt_report" in st.session_state or st.session_state.get("_qvt_figures"):
        st.markdown("<br>", unsafe_allow_html=True)
        render_zip_button(
            docx_bytes=st.session_state.get("_qvt_report"),
            figures=st.session_state.get("_qvt_figures", {}),
            prefix="qvt", company=company_qvt,
            label="📦 Télécharger tout (ZIP)",
        )

if len(df) == 0:
    st.warning("Aucun répondant ne correspond aux filtres sélectionnés.")
    st.stop()

# `metrics` contient toute la matière première du dashboard.
# Les onglets suivants se contentent de présenter ces résultats.
# ─── ANALYTICS ───────────────────────────────────────────────────────────────
q_engine = QVTQuestionnaire()
metrics  = q_engine.analytics(df)
demo     = metrics["demographics"]
dims     = metrics["dimensions"]
glb      = metrics.get("global", {})

# ─── ONGLETS ─────────────────────────────────────────────────────────────────
tab_overview, tab_dims, tab_cross = st.tabs(["Vue d'ensemble", "Dimensions QVT", "Croisement"])


# =============================================================================
# TAB 1 — VUE D'ENSEMBLE
# =============================================================================
with tab_overview:
    section_title("Population & Score Global")

    total_n = demo["total"]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(html_kpi(total_n, "Effectif total",
            icon=svg_icon("M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9.5 7a3 3 0 1 0 0-6 3 3 0 0 0 0 6", "rgba(34,197,94,0.1)", "#22C55E")), unsafe_allow_html=True)
    with c2:
        st.markdown(html_kpi(demo["men"]["pct"], "Hommes", suffix="%", subtitle=f"{demo['men']['n']}",
            icon=svg_icon("M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4M5 21a7 7 0 0 1 14 0", "rgba(56,163,232,0.1)", "#38A3E8")), unsafe_allow_html=True)
    with c3:
        st.markdown(html_kpi(demo["women"]["pct"], "Femmes", suffix="%", subtitle=f"{demo['women']['n']}",
            icon=svg_icon("M12 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4M8 15h8l1.5 6h-11z", "rgba(249,115,22,0.1)", "#F97316")), unsafe_allow_html=True)
    with c4:
        st.markdown(html_kpi(demo["avg_age"], "Âge moyen", suffix=" ans",
            icon=svg_icon("M8 2v4M16 2v4M3 10h18M5 6h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z", "rgba(249,115,22,0.1)", "#F97316")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Score global KPI
    if glb:
        section_title("Score QVT Global")
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.markdown(html_kpi(glb.get("mean", 0), "Score moyen", decimals=2,
                icon=svg_icon("M9 19v-6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2zm0 0V9a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v10m-6 0a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2m0 0V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v14a2 2 0 0 0-2 2h-2a2 2 0 0 0-2-2z", "rgba(34,197,94,0.1)", "#22C55E")), unsafe_allow_html=True)
        with col_g2:
            st.markdown(html_kpi(glb.get("median", 0), "Médiane", decimals=2,
                icon=svg_icon("M3 12h18M3 6h18M3 18h18", "rgba(56,163,232,0.1)", "#38A3E8")), unsafe_allow_html=True)
        with col_g3:
            pct_sat = glb.get("pct_satisfaisant", 0)
            st.markdown(html_kpi(pct_sat, "% Satisfaisants", suffix="%",
                icon=svg_icon("M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0", "rgba(34,197,94,0.1)", "#22C55E")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Radar des dimensions
    section_title("Profil QVT par dimension")
    dim_scores = {}
    for dim, data in dims.items():
        cats = data.get("categories", {})
        dim_scores[data["label"]] = cats.get("Satisfaisant", {}).get("pct", 0)

    with st.container(border=True):
        rc1, rc2 = st.columns([6, 4])
        with rc1:
            fig_radar = make_radar(dim_scores, list(dim_scores.keys()))
            st.plotly_chart(fig_radar, use_container_width=True, key="qvt_radar")
        with rc2:
            st.markdown("<br>", unsafe_allow_html=True)
            for dim_key, data in dims.items():
                cats = data.get("categories", {})
                pct_sat = cats.get("Satisfaisant", {}).get("pct", 0)
                n_sat   = cats.get("Satisfaisant", {}).get("n", 0)
                color   = "#22C55E" if pct_sat >= 60 else "#EF4444" if pct_sat < 40 else "#F97316"
                st.markdown(html_prog(data["label"], pct_sat, color, n_sat), unsafe_allow_html=True)


# =============================================================================
# TAB 2 — DIMENSIONS QVT
# =============================================================================
with tab_dims:
    section_title("Résultats détaillés par dimension")

    # Jauges par dimension
    dim_list = list(dims.items())
    rows = [dim_list[i:i+3] for i in range(0, len(dim_list), 3)]
    for row in rows:
        cols = st.columns(len(row))
        for col, (dim_key, data) in zip(cols, row):
            mean_val = data.get("mean", 0)
            # QVT échelle 1-5 : max par item = 5
            # max_score dépend du nombre d'items de la dimension
            n_items = len([k for k in ["Q1", "Q2", "Q3", "Q4"] if f"{k}_{dim_key}" in df.columns]) or 3
            max_score = 5 * n_items
            cats = data.get("categories", {})
            pct_sat = cats.get("Satisfaisant", {}).get("pct", 0)
            color = "#22C55E" if pct_sat >= 60 else "#EF4444" if pct_sat < 40 else "#F97316"
            with col:
                st.markdown(html_gauge_raw(mean_val, 5, data["label"], f"n = {data.get('n', 0)}", color=color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Distribution des catégories par dimension
    section_title("Répartition Satisfaisant / Mitigé / Insatisfaisant")

    fig_dims = go.Figure()
    cat_colors = {"Satisfaisant": "#22C55E", "Mitigé": "#F97316", "Insatisfaisant": "#EF4444"}
    dim_labels = [data["label"] for _, data in dims.items()]

    for cat, color in cat_colors.items():
        vals = []
        for dim_key, data in dims.items():
            cats = data.get("categories", {})
            vals.append(cats.get(cat, {}).get("pct", 0))
        fig_dims.add_trace(go.Bar(
            name=cat, x=dim_labels, y=vals,
            marker_color=color, opacity=0.9,
            text=[f"{v:.0f}%" for v in vals], textposition="auto",
            textfont=dict(color="white", size=11),
        ))

    _plotly_base(fig_dims, height=420)
    fig_dims.update_layout(
        barmode="group",
        xaxis=dict(title_text="Dimension"),
        yaxis=dict(title_text="Pourcentage (%)"),
        legend=dict(title_text="Catégorie"),
    )
    st.plotly_chart(fig_dims, use_container_width=True, key="qvt_bar_dims")

    # Tableau de synthèse
    section_title("Tableau de synthèse")
    rows_tbl = []
    for dim_key, data in dims.items():
        cats = data.get("categories", {})
        rows_tbl.append({
            "Dimension":       data["label"],
            "Score moyen":     data.get("mean", 0),
            "n":               data.get("n", 0),
            "% Satisfaisant":  round(cats.get("Satisfaisant", {}).get("pct", 0), 1),
            "% Mitigé":        round(cats.get("Mitigé", {}).get("pct", 0), 1),
            "% Insatisfaisant":round(cats.get("Insatisfaisant", {}).get("pct", 0), 1),
        })
    df_tbl = pd.DataFrame(rows_tbl)

    def _color_pct(val):
        color = "#22C55E" if val >= 60 else "#EF4444" if val < 40 else "#F97316"
        return f"color: {color}; font-weight: 700"

    styled = df_tbl.style.applymap(_color_pct, subset=["% Satisfaisant"]) \
                        .applymap(lambda v: "color:#EF4444;font-weight:700" if v > 30 else "", subset=["% Insatisfaisant"]) \
                        .format({"Score moyen": "{:.2f}", "% Satisfaisant": "{:.1f}%", "% Mitigé": "{:.1f}%", "% Insatisfaisant": "{:.1f}%"})
    st.dataframe(styled, use_container_width=True, hide_index=True)


# =============================================================================
# TAB 3 — CROISEMENT
# =============================================================================
with tab_cross:
    section_title("Exploration des données")

    csp_actual = next((c for c in df.columns if re.search(r"categorie.*socio|csp", _norm(c))), None)

    VAR_MAP = {
        "Genre":                         "Genre",
        "Tranche d'âge":                 "Tranche_age",
        "Ancienneté":                    "Tranche_anciennete",
        "Direction":                     "Direction",
    }
    if csp_actual:
        VAR_MAP["Catégorie socioprofessionnelle"] = csp_actual

    CROSS_MAP: dict = {"Aucun croisement": None}
    for dim_key in DIMENSIONS:
        col = f"{dim_key}_score_cat"
        if col in df.columns:
            CROSS_MAP[DIMENSIONS[dim_key]] = col

    avail_vars  = [k for k, v in VAR_MAP.items()  if v and v in df.columns]
    avail_cross = [k for k, v in CROSS_MAP.items() if v is None or (v and v in df.columns)]

    if not avail_vars:
        st.info("Aucune variable démographique détectée dans le fichier.")
    else:
        cx1, cx2 = st.columns(2)
        with cx1:
            sel_var   = st.selectbox("Variable à visualiser", avail_vars,  key="qvt_cr_var")
        with cx2:
            sel_cross = st.selectbox("Croiser avec (optionnel)", avail_cross, key="qvt_cr_cross")

        real_col  = VAR_MAP.get(sel_var)
        cross_col = CROSS_MAP.get(sel_cross)

        if real_col and real_col in df.columns:
            if cross_col and cross_col in df.columns:
                fig_cr = make_stacked(df, real_col, cross_col)
                if fig_cr:
                    st.plotly_chart(fig_cr, use_container_width=True, key="qvt_cr_stacked")
                    tmp = df[[real_col, cross_col]].dropna()
                    if not tmp.empty:
                        pct_tbl = pd.crosstab(tmp[real_col].astype(str), tmp[cross_col].astype(str), normalize="index").mul(100).round(1)
                        st.dataframe(pct_tbl.style.format("{:.1f}%"), use_container_width=True)
                else:
                    st.info("Données insuffisantes.")
            else:
                fig_bar = make_barplot(df, real_col)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True, key="qvt_cr_bar")
