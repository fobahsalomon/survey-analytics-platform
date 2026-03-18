"""
pages/3_mbi.py
Dashboard MBI Burnout — Maslach Burnout Inventory (MBI-GS)
Utilise lib/questionnaires/mbi comme engine backend.
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

from lib.questionnaires.mbi import MBIQuestionnaire, MBIReporting, MBIVisualizations
from lib.questionnaires.mbi.config import DIMENSIONS, THRESHOLDS, MBI_COLORS, BURNOUT_RISK_LEVELS
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
    page_title="MBI Burnout · Wave-CI",
    page_icon="🔥",
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
        '0 4px 12px rgba(249,115,22,0.08);border:1px solid #e8edf5;">'
        '<div style="width:38px;height:38px;background:linear-gradient(135deg,#C2410C,#F97316);'
        'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        '<i class="fas fa-fire" style="color:white;font-size:15px;"></i></div>'
        '<div>'
        '<div style="font-size:16px;font-weight:700;color:#1e293b;">MBI — Maslach Burnout Inventory (MBI-GS)</div>'
        '<div style="font-size:11px;color:#64748b;margin-top:1px;">Épuisement émotionnel · Cynisme · Efficacité personnelle — Schaufeli et al., 1996</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
with _col_back:
    if st.button("← Accueil", key="back_home_mbi", use_container_width=True):
        st.switch_page("app.py")

# ─── UPLOAD ──────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Charger un fichier Excel ou CSV",
    type=["xlsx", "xls", "csv"],
    key="mbi_uploader",
)
if uploaded is not None:
    st.session_state["_mbi_bytes"] = uploaded.read()
    st.session_state["_mbi_name"]  = uploaded.name

if "_mbi_bytes" not in st.session_state:
    st.info("Veuillez charger un fichier de données pour démarrer l'analyse MBI.")
    st.stop()

# ─── PIPELINE ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_pipeline(file_bytes: bytes, file_name: str, _v: int = 1):
    q  = MBIQuestionnaire()
    df = load_dataframe(io.BytesIO(file_bytes), file_name=file_name)
    return q.run(df)

with st.spinner("Traitement des données…"):
    df_scored = run_pipeline(st.session_state["_mbi_bytes"], st.session_state["_mbi_name"])

# ─── SIDEBAR FILTRES ─────────────────────────────────────────────────────────
df = render_sidebar(df_scored, prefix="mbi")

with st.sidebar:
    n_f = len(df)
    st.markdown(f"""<div style="text-align:center;padding:0.7rem;background:#FEF3C7;border-radius:10px;margin-top:0.8rem;">
    <span style="font-size:0.7rem;color:#92400E;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Effectif filtré</span><br>
    <span style="font-size:1.6rem;font-weight:800;color:#F97316;">{n_f}</span>
    </div>""", unsafe_allow_html=True)

    # Export
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<span style="font-size:0.7rem;font-weight:700;color:#6B88A8;text-transform:uppercase;letter-spacing:0.08em;">Export</span>', unsafe_allow_html=True)
    company_mbi = st.text_input("Nom organisation", value="Mon Organisation", key="mbi_company")
    if st.button("Générer rapport + visuels", key="mbi_gen_report", use_container_width=True):
        with st.spinner("Génération des visualisations…"):
            try:
                viz_mbi = MBIVisualizations(company=company_mbi)
                q_tmp   = MBIQuestionnaire()
                m_tmp   = q_tmp.analytics(df)
                figs_mbi = viz_mbi.generate_all(df, m_tmp)
                st.session_state["_mbi_figures"] = figs_mbi
            except Exception as e:
                st.warning(f"Visualisations partielles : {e}")
                st.session_state["_mbi_figures"] = {}
        with st.spinner("Génération du rapport Word…"):
            try:
                q_engine = MBIQuestionnaire()
                metrics  = q_engine.analytics(df)
                reporter = MBIReporting(company_name=company_mbi)
                docx_bytes = reporter.generate(
                    metrics,
                    figures=st.session_state.get("_mbi_figures", {}),
                )
                st.session_state["_mbi_report"] = docx_bytes
                n_figs = len(st.session_state.get("_mbi_figures", {}))
                st.success(f"Rapport prêt — {n_figs} figure(s) incluse(s)")
            except ImportError as e:
                st.error(f"python-docx manquant : {e}")
            except Exception as e:
                st.error(f"Erreur rapport : {e}")
    if "_mbi_report" in st.session_state:
        render_export_button(st.session_state["_mbi_report"], "rapport_mbi.docx")
    if "_mbi_report" in st.session_state or st.session_state.get("_mbi_figures"):
        st.markdown("<br>", unsafe_allow_html=True)
        render_zip_button(
            docx_bytes=st.session_state.get("_mbi_report"),
            figures=st.session_state.get("_mbi_figures", {}),
            prefix="mbi", company=company_mbi,
            label="📦 Télécharger tout (ZIP)",
        )

if len(df) == 0:
    st.warning("Aucun répondant ne correspond aux filtres sélectionnés.")
    st.stop()

# ─── ANALYTICS ───────────────────────────────────────────────────────────────
q_engine    = MBIQuestionnaire()
metrics     = q_engine.analytics(df)
demo        = metrics["demographics"]
dims        = metrics["dimensions"]
burnout_risk= metrics.get("burnout_risk", {})

# ─── ONGLETS ─────────────────────────────────────────────────────────────────
tab_overview, tab_dims, tab_cross = st.tabs(["Vue d'ensemble", "Dimensions MBI", "Croisement"])


# =============================================================================
# TAB 1 — VUE D'ENSEMBLE
# =============================================================================
with tab_overview:
    section_title("Population & Risque de Burnout")

    # KPIs population
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(html_kpi(demo["total"], "Effectif total",
            icon=svg_icon("M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9.5 7a3 3 0 1 0 0-6 3 3 0 0 0 0 6", "rgba(249,115,22,0.1)", "#F97316")), unsafe_allow_html=True)
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

    # Risque burnout global
    section_title("Risque global de Burnout")
    st.markdown("""
    <div style="background:rgba(249,115,22,0.06);border:1px solid rgba(249,115,22,0.2);border-radius:12px;
    padding:0.9rem 1.2rem;margin-bottom:1rem;font-size:0.86rem;color:#7C3A00;line-height:1.6;">
    <strong>Rappel méthodologique :</strong> Le burnout composite est estimé à partir des 3 dimensions MBI-GS.
    Un profil à risque élevé présente simultanément un épuisement élevé, un cynisme élevé <em>et</em> une efficacité personnelle faible.
    Ces seuils sont indicatifs — ils ne constituent pas un diagnostic clinique.
    </div>""", unsafe_allow_html=True)

    if burnout_risk:
        br1, br2, br3 = st.columns(3)
        risk_colors = {"Faible": "#22C55E", "Modéré": "#F97316", "Élevé": "#EF4444"}
        for col, (level, data) in zip([br1, br2, br3], burnout_risk.items()):
            color = risk_colors.get(level, "#94A3B8")
            with col:
                st.markdown(html_zone(f"Risque {level}", data["pct"], data["n"], color), unsafe_allow_html=True)
    else:
        st.info("Score de risque composite non disponible — vérifiez que le fichier contient les 3 dimensions MBI.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Jauges des 3 dimensions
    section_title("Scores par dimension (moyenne sur échelle 0–6)")
    dg1, dg2, dg3 = st.columns(3)
    dim_cols_list = [("exhaustion", dg1), ("cynicism", dg2), ("efficacy", dg3)]
    dim_colors = {"exhaustion": "#EF4444", "cynicism": "#F97316", "efficacy": "#22C55E"}
    dim_sublabels = {
        "exhaustion": "Score élevé = risque",
        "cynicism":   "Score élevé = risque",
        "efficacy":   "Score faible = risque",
    }
    for dim_key, col_widget in dim_cols_list:
        data  = dims.get(dim_key, {})
        mean  = data.get("mean", 0)
        n     = data.get("n", 0)
        color = dim_colors[dim_key]
        cats  = data.get("categories", {})
        pct_eleve = cats.get("Élevé", {}).get("pct", 0)
        badge = f"{pct_eleve:.0f}% élevé"
        with col_widget:
            st.markdown(
                html_gauge_raw(mean, 6, DIMENSIONS[dim_key], dim_sublabels[dim_key], color=color, badge_text=badge),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Barres de progression
    section_title("Répartition Bas / Modéré / Élevé par dimension")
    for dim_key, data in dims.items():
        cats = data.get("categories", {})
        with st.expander(f"**{data['label']}** — moyenne : {data.get('mean', 0):.2f}", expanded=True):
            pc1, pc2, pc3 = st.columns(3)
            for col_w, cat, color in [(pc1, "Bas", "#22C55E"), (pc2, "Modéré", "#F97316"), (pc3, "Élevé", "#EF4444")]:
                d = cats.get(cat, {"pct": 0, "n": 0})
                with col_w:
                    st.markdown(html_ls_n(d["pct"], d["n"], cat), unsafe_allow_html=True)


# =============================================================================
# TAB 2 — DIMENSIONS MBI
# =============================================================================
with tab_dims:
    section_title("Analyse détaillée des dimensions")

    # Graphique comparatif groupé
    fig_mbi = go.Figure()
    cat_colors = {"Bas": "#22C55E", "Modéré": "#F97316", "Élevé": "#EF4444"}
    dim_labels_list = [data["label"] for _, data in dims.items()]

    for cat, color in cat_colors.items():
        vals = []
        ns   = []
        for dim_key, data in dims.items():
            cats = data.get("categories", {})
            vals.append(cats.get(cat, {}).get("pct", 0))
            ns.append(cats.get(cat, {}).get("n", 0))
        fig_mbi.add_trace(go.Bar(
            name=cat, x=dim_labels_list, y=vals,
            marker_color=color, opacity=0.9,
            text=[f"{v:.0f}%\n({n})" for v, n in zip(vals, ns)],
            textposition="auto",
            textfont=dict(color="white", size=10),
        ))

    _plotly_base(fig_mbi, height=420)
    fig_mbi.update_layout(
        barmode="group",
        xaxis_title="Dimension MBI",
        yaxis_title="Pourcentage (%)",
        legend_title_text="Niveau",
    )
    st.plotly_chart(fig_mbi, use_container_width=True, key="mbi_bar_dims")

    # Tableau
    section_title("Tableau de synthèse")
    rows_tbl = []
    for dim_key, data in dims.items():
        cats = data.get("categories", {})
        rows_tbl.append({
            "Dimension":    data["label"],
            "Score moyen":  data.get("mean", 0),
            "n":            data.get("n", 0),
            "% Bas":        round(cats.get("Bas",    {}).get("pct", 0), 1),
            "% Modéré":     round(cats.get("Modéré", {}).get("pct", 0), 1),
            "% Élevé":      round(cats.get("Élevé",  {}).get("pct", 0), 1),
        })
    df_tbl = pd.DataFrame(rows_tbl)
    styled = df_tbl.style \
        .applymap(lambda v: "color:#22C55E;font-weight:700" if v >= 60 else "", subset=["% Bas"]) \
        .applymap(lambda v: "color:#EF4444;font-weight:700" if v > 30 else "", subset=["% Élevé"]) \
        .format({"Score moyen": "{:.2f}", "% Bas": "{:.1f}%", "% Modéré": "{:.1f}%", "% Élevé": "{:.1f}%"})
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Avertissement si burnout élevé
    if burnout_risk:
        pct_eleve = burnout_risk.get("Élevé", {}).get("pct", 0)
        if pct_eleve > 20:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.3);
            border-radius:12px;padding:1rem 1.4rem;margin-top:1rem;">
            <strong style="color:#B91C1C;">⚠ Alerte :</strong>
            <span style="color:#7F1D1D;font-size:0.9rem;">
            {pct_eleve:.1f}% des répondants présentent un profil de burnout à risque élevé.
            Une attention particulière est recommandée.
            </span></div>""", unsafe_allow_html=True)


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
    if "burnout_risk" in df.columns:
        CROSS_MAP["Risque Burnout"] = "burnout_risk"

    avail_vars  = [k for k, v in VAR_MAP.items()  if v and v in df.columns]
    avail_cross = [k for k, v in CROSS_MAP.items() if v is None or (v and v in df.columns)]

    if not avail_vars:
        st.info("Aucune variable démographique détectée dans le fichier.")
    else:
        cx1, cx2 = st.columns(2)
        with cx1:
            sel_var   = st.selectbox("Variable à visualiser", avail_vars,  key="mbi_cr_var")
        with cx2:
            sel_cross = st.selectbox("Croiser avec (optionnel)", avail_cross, key="mbi_cr_cross")

        real_col  = VAR_MAP.get(sel_var)
        cross_col = CROSS_MAP.get(sel_cross)

        if real_col and real_col in df.columns:
            if cross_col and cross_col in df.columns:
                fig_cr = make_stacked(df, real_col, cross_col)
                if fig_cr:
                    st.plotly_chart(fig_cr, use_container_width=True, key="mbi_cr_stacked")
                    tmp = df[[real_col, cross_col]].dropna()
                    if not tmp.empty:
                        pct_tbl = pd.crosstab(tmp[real_col].astype(str), tmp[cross_col].astype(str), normalize="index").mul(100).round(1)
                        st.dataframe(pct_tbl.style.format("{:.1f}%"), use_container_width=True)
                else:
                    st.info("Données insuffisantes.")
            else:
                fig_bar = make_barplot(df, real_col)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True, key="mbi_cr_bar")
