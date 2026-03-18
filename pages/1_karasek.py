"""
pages/1_karasek.py
Dashboard Karasek — Demande–Contrôle–Soutien
Utilise lib/questionnaires/karasek comme engine backend.
"""

import sys
import re
import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st
import warnings

warnings.filterwarnings("ignore")

# ── path resolution ──────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Chaque page Streamlit importe son module questionnaire comme un "moteur".
# La page pilote l'expérience utilisateur, mais les calculs restent dans `lib/`.
from lib.questionnaires.karasek import KarasekQuestionnaire, KarasekReporting, KarasekVisualizations
from lib.questionnaires.karasek.config import THRESHOLDS, KARASEK_COLORS, SCORE_LABELS, RH_SCORE_GROUPS
from pages._export_utils import render_zip_button, build_zip
from lib.common.file_utils import load_dataframe
from pages._ui_shared import (
    inject_css, inject_animation_js,
    section_title, svg_icon, html_kpi, html_gauge, html_prog,
    html_zone, html_ls_n, make_barplot, make_stacked, make_radar,
    _plotly_base, fig_to_png, render_sidebar, render_export_button,
    _norm, _clean_opts,
)

st.set_page_config(
    page_title="Karasek DCS · SurveyLens",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
inject_animation_js()

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800'
    '&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# ─── TOPBAR ──────────────────────────────────────────────────────────────────
_col_top, _col_back = st.columns([9, 1])
with _col_top:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;background:white;border-radius:12px;'
        'padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),'
        '0 4px 12px rgba(30,110,79,0.08);border:1px solid #e8edf5;">'
        '<div style="width:38px;height:38px;background:linear-gradient(135deg,#DC2626,#EF4444);'
        'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        '<i class="fas fa-brain" style="color:white;font-size:15px;"></i></div>'
        '<div>'
        '<div style="font-size:16px;font-weight:700;color:#1e293b;">Modèle de Karasek — Demande–Contrôle–Soutien</div>'
        '<div style="font-size:11px;color:#64748b;margin-top:1px;">Analyse des risques psychosociaux au travail (Job Strain & Iso-Strain)</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
with _col_back:
    if st.button("← Accueil", key="back_home_k", use_container_width=True):
        st.switch_page("app.py")

# ─── UPLOAD ──────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Charger un fichier Excel ou CSV",
    type=["xlsx", "xls", "csv"],
    key="karasek_uploader",
)
if uploaded is not None:
    st.session_state["_k_bytes"] = uploaded.read()
    st.session_state["_k_name"]  = uploaded.name

if "_k_bytes" not in st.session_state:
    st.info("Veuillez charger un fichier de données (Excel ou CSV) pour démarrer l'analyse.")
    st.stop()

# ─── PIPELINE ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_pipeline(file_bytes: bytes, file_name: str, _v: int = 1):
    """Charge, nettoie, score et classe un fichier Karasek."""
    # Ce cache évite de recalculer tout le pipeline à chaque interaction UI
    # quand le fichier source n'a pas changé.
    q  = KarasekQuestionnaire()
    df = load_dataframe(io.BytesIO(file_bytes), file_name=file_name)
    df = q.run(df)
    return df

with st.spinner("Traitement des données…"):
    df_scored = run_pipeline(st.session_state["_k_bytes"], st.session_state["_k_name"])

# ─── SIDEBAR FILTRES ─────────────────────────────────────────────────────────
df = render_sidebar(df_scored, prefix="k")

with st.sidebar:
    n_f = len(df)
    st.markdown(f"""<div style="text-align:center;padding:0.7rem;background:#EDF5FD;border-radius:10px;margin-top:0.8rem;">
    <span style="font-size:0.7rem;color:#6B88A8;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Effectif filtré</span><br>
    <span style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.6rem;font-weight:800;color:#38A3E8;"
        class="animate-number" data-target="{n_f}">{n_f}</span>
    </div>""", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("Aucun répondant ne correspond aux filtres sélectionnés.")
    st.stop()

# À partir d'ici, on ne travaille plus sur des réponses brutes.
# `metrics` contient déjà des résumés prêts à être affichés dans le dashboard.
# ─── ANALYTICS ───────────────────────────────────────────────────────────────
q_engine  = KarasekQuestionnaire()
metrics   = q_engine.analytics(df)
demo      = metrics["demographics"]
lifestyle = metrics["lifestyle"]
quadrants = metrics["quadrants"]
stress    = metrics["stress_indicators"]
strain    = metrics["strain_prevalence"]
rh        = metrics["rh_scores"]

# Les exports réutilisent les mêmes métriques que l'écran.
# Cela évite d'avoir deux logiques métier différentes entre UI et rapport.
# ─── EXPORT WORD + ZIP (sidebar) ────────────────────────────────────────────
with st.sidebar:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<span style="font-size:0.7rem;font-weight:700;color:#6B88A8;'
        'text-transform:uppercase;letter-spacing:0.08em;">Export</span>',
        unsafe_allow_html=True,
    )
    company = st.text_input("Nom organisation", value="Mon Organisation", key="k_company")

    if st.button("Générer rapport + visuels", key="k_gen_report", use_container_width=True):
        with st.spinner("Génération des visualisations…"):
            try:
                viz    = KarasekVisualizations(company=company)
                figs   = viz.generate_all(df, metrics)
                st.session_state["_k_figures"] = figs
            except Exception as e:
                st.warning(f"Visualisations partielles : {e}")
                st.session_state["_k_figures"] = {}

        with st.spinner("Génération du rapport Word…"):
            try:
                reporter = KarasekReporting(company_name=company)
                docx_b   = reporter.generate(
                    metrics,
                    figures=st.session_state.get("_k_figures", {}),
                )
                st.session_state["_k_report"] = docx_b
                n_figs = len(st.session_state.get("_k_figures", {}))
                st.success(f"Rapport prêt — {n_figs} figure(s) incluse(s)")
            except ImportError as e:
                st.error(f"python-docx manquant : {e}")
            except Exception as e:
                st.error(f"Erreur rapport : {e}")

    # Bouton Word seul
    if "_k_report" in st.session_state:
        render_export_button(st.session_state["_k_report"], "rapport_karasek.docx")

    # Bouton ZIP (rapport + toutes les figures)
    if "_k_report" in st.session_state or st.session_state.get("_k_figures"):
        st.markdown("<br>", unsafe_allow_html=True)
        render_zip_button(
            docx_bytes=st.session_state.get("_k_report"),
            figures=st.session_state.get("_k_figures", {}),
            prefix="karasek",
            company=company,
            label="📦 Télécharger tout (ZIP)",
        )

# ─── ONGLETS ─────────────────────────────────────────────────────────────────
tab_gen, tab_quad, tab_cross = st.tabs(["Vue d'ensemble", "Stress & Quadrants", "Croisement"])


# =============================================================================
# TAB 1 — VUE D'ENSEMBLE
# =============================================================================
with tab_gen:
    section_title("Données Générales de la Population")

    total_n  = demo["total"]
    n_men    = demo["men"]["n"]
    n_women  = demo["women"]["n"]
    avg_age  = demo["avg_age"]

    from lib.common.common_cleaning import find_col_by_pattern
    sit_col = find_col_by_pattern(list(df.columns), [r"situation.*matrimon"])
    if sit_col:
        sv = df[sit_col].value_counts(dropna=True)
        sit_top, sit_n = (str(sv.index[0]), int(sv.iloc[0])) if not sv.empty else ("N/A", 0)
        sit_pct = sit_n / total_n * 100 if total_n > 0 else 0.0
    else:
        sit_top, sit_n, sit_pct = "N/A", 0, 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(html_kpi(total_n, "Effectif total",
            icon=svg_icon("M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2M9.5 7a3 3 0 1 0 0-6 3 3 0 0 0 0 6M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a3 3 0 0 1 0 5.75", "rgba(56,163,232,0.1)", "#38A3E8")), unsafe_allow_html=True)
    with c2:
        st.markdown(html_kpi(n_men / total_n * 100 if total_n else 0, "Hommes", suffix="%", subtitle=f"{n_men}",
            icon=svg_icon("M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4M5 21a7 7 0 0 1 14 0", "rgba(56,163,232,0.1)", "#38A3E8")), unsafe_allow_html=True)
    with c3:
        st.markdown(html_kpi(n_women / total_n * 100 if total_n else 0, "Femmes", suffix="%", subtitle=f"{n_women}",
            icon=svg_icon("M12 11a4 4 0 1 0-4-4 4 4 0 0 0 4 4M8 15h8l1.5 6h-11zM12 15v6", "rgba(249,115,22,0.1)", "#F97316")), unsafe_allow_html=True)
    with c4:
        st.markdown(html_kpi(avg_age, "Âge moyen", suffix=" ans",
            icon=svg_icon("M8 2v4M16 2v4M3 10h18M5 6h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z", "rgba(249,115,22,0.1)", "#F97316")), unsafe_allow_html=True)
    with c5:
        st.markdown(html_kpi(sit_pct, "Situation matrimoniale", suffix="%", subtitle=f"{sit_top} — {sit_n}",
            icon=svg_icon("M12 21.7C5.4 21.7 2 16.4 2 12S5.4 2.3 12 2.3 22 7.6 22 12s-3.4 9.7-10 9.7z", "rgba(34,197,94,0.1)", "#22C55E")), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Modes de vie
    section_title("Indicateurs de modes de vie")
    cl1, cl2, cl3, cl4 = st.columns(4)
    with cl1:
        d = lifestyle.get("tobacco", {"pct": 0, "n": 0})
        st.markdown(html_ls_n(d["pct"], d["n"], "Tabagisme"), unsafe_allow_html=True)
    with cl2:
        d = lifestyle.get("alcohol", {"pct": 0, "n": 0})
        st.markdown(html_ls_n(d["pct"], d["n"], "Consommation d'alcool"), unsafe_allow_html=True)
    with cl3:
        d = lifestyle.get("sedentarity", {"pct": 0, "n": 0})
        st.markdown(html_ls_n(d["pct"], d["n"], "Sédentarité"), unsafe_allow_html=True)
    with cl4:
        d = lifestyle.get("overweight", {"pct": 0, "n": 0})
        st.markdown(html_ls_n(d["pct"], d["n"], "Surpoids & Obésité"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Satisfaction organisationnelle
    section_title("Satisfaction organisationnelle")
    DIMS_ORG = [
        ("rec_score", "Reconnaissance"), ("equ_score", "Équité de charge"),
        ("cult_score", "Culture d'entreprise"), ("sat_score", "Satisfaction"),
        ("adq_resources_score", "Ressources & Objectifs"), ("sup_score", "Soutien management"),
        ("adq_role_score", "Formation"), ("comp_score", "Compétences"),
    ]
    dim_pcts  = {lbl: rh.get(sc, {}).get("pct", 0) for sc, lbl in DIMS_ORG}
    dim_stats = {lbl: (rh.get(sc, {}).get("pct", 0), rh.get(sc, {}).get("n", 0)) for sc, lbl in DIMS_ORG}

    with st.container(border=True):
        st.markdown('<p style="color:#4E6A88;font-size:0.98rem;margin:0.12rem 0 0.65rem;">% de collaborateurs avec un niveau élevé de satisfaction par dimension</p>', unsafe_allow_html=True)
        rc1, rc2 = st.columns([6, 4])
        with rc1:
            st.plotly_chart(make_radar(dim_pcts, [d[1] for d in DIMS_ORG]), use_container_width=True, key="k_radar_gen")
        with rc2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            bars_html = "".join(
                html_prog(lbl, pct, "#22C55E" if pct > 50 else "#EF4444", n)
                for lbl, (pct, n) in dim_stats.items()
            )
            st.markdown(bars_html, unsafe_allow_html=True)


# =============================================================================
# TAB 2 — STRESS & QUADRANTS
# =============================================================================
with tab_quad:
    section_title("Indicateurs clés de stress au travail")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(html_gauge(stress["autonomy"]["pct"],       "Autonomie décisionnelle", "Flexibilité et contrôle perçus",       inverted=False), unsafe_allow_html=True)
    with g2:
        st.markdown(html_gauge(stress["workload"]["pct"],       "Charge mentale perçue",   "Intensité de la demande psychologique", inverted=True),  unsafe_allow_html=True)
    with g3:
        st.markdown(html_gauge(stress["social_support"]["pct"], "Cohésion d'équipe",        "Soutien social collègues & management", inverted=False), unsafe_allow_html=True)

    # Strain KPIs
    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Prévalence du Job Strain & Iso-Strain")
    sk1, sk2, sk3, sk4 = st.columns(4)
    with sk1:
        d = strain.get("Job_strain", {"pct": 0, "n": 0})
        st.markdown(html_ls_n(d["pct"], d["n"], "Job Strain"), unsafe_allow_html=True)
    with sk2:
        d = strain.get("Iso_strain", {"pct": 0, "n": 0})
        st.markdown(html_ls_n(d["pct"], d["n"], "Iso-Strain"), unsafe_allow_html=True)

    # Quadrants
    section_title("Répartition par quadrant Karasek")
    quad_col = "Karasek_quadrant_theoretical"
    if quad_col in df.columns:
        qc1, qc2, qc3, qc4 = st.columns(4)
        tv = len(df.dropna(subset=[quad_col]))
        aliases = {"Tendu": ["Tendu"], "Actif": ["Actif"], "Passif": ["Passif"], "Détendu": ["Detendu", "Détendu"]}
        zone_colors = {"Tendu": "#EF4444", "Actif": "#22C55E", "Passif": "#94A3B8", "Détendu": "#38A3E8"}
        for raw, cui in [("Tendu", qc1), ("Actif", qc2), ("Passif", qc3), ("Détendu", qc4)]:
            n = int(df[quad_col].isin(aliases[raw]).sum())
            with cui:
                st.markdown(html_zone(raw, n / tv * 100 if tv > 0 else 0, n, zone_colors[raw]), unsafe_allow_html=True)
    else:
        st.info("Scores Karasek manquants — vérifiez que le fichier contient les items Dem/Lat/SS.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Grille MAPP
    section_title("Grille MAPP du Stress")
    st.markdown('<p style="color:#4E6A88;font-size:0.98rem;margin-top:-0.3rem;">Chaque point représente un agent. Les axes délimitent les zones du quadrant Karasek.</p>', unsafe_allow_html=True)

    if quad_col in df.columns and "Dem_score" in df.columns and "Lat_score" in df.columns:
        df_p = df[["Dem_score", "Lat_score", quad_col]].dropna().copy()
        if not df_p.empty:
            qmap = {"Actif": "Actif", "Detendu": "Détendu", "Détendu": "Détendu", "Tendu": "Tendu", "Passif": "Passif"}
            df_p["quad_display"] = df_p[quad_col].map(qmap).fillna(df_p[quad_col])
            cmap = {"Actif": "#22C55E", "Détendu": "#38A3E8", "Tendu": "#EF4444", "Passif": "#94A3B8"}
            fig_sc = px.scatter(
                df_p, x="Lat_score", y="Dem_score", color="quad_display",
                color_discrete_map=cmap, opacity=0.75,
                labels={"Lat_score": "Latitude décisionnelle", "Dem_score": "Demande psychologique", "quad_display": "Zone"},
                custom_data=["quad_display", "Lat_score", "Dem_score"],
            )
            fig_sc.update_traces(
                marker=dict(size=8, line=dict(width=1, color="white")),
                hovertemplate="<b>Zone</b>: %{customdata[0]}<br>Autonomie: %{customdata[1]:.1f}<br>Charge: %{customdata[2]:.1f}<extra></extra>",
            )
            fig_sc.add_vline(x=THRESHOLDS["Lat_score"], line_dash="dot", line_color="rgba(249,115,22,0.45)", line_width=1.8)
            fig_sc.add_hline(y=THRESHOLDS["Dem_score"], line_dash="dot", line_color="rgba(249,115,22,0.45)", line_width=1.8)
            _plotly_base(fig_sc, height=500)
            fig_sc.update_layout(
                xaxis_title="Latitude décisionnelle (autonomie & compétences)",
                yaxis_title="Demande psychologique (charge mentale)",
                legend_title_text="Zone",
            )
            st.plotly_chart(fig_sc, use_container_width=True, key="k_mapp_chart")
        else:
            st.info("Données insuffisantes pour la grille MAPP.")
    else:
        st.warning("Colonnes manquantes pour la grille MAPP.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Heatmap par direction
    dir_col_hm = next((c for c in df.columns if re.search(r"^direction$", _norm(c))), None)
    if dir_col_hm and quad_col in df.columns:
        section_title("Heatmap Karasek par Direction")
        ct_hm = pd.crosstab(df[dir_col_hm], df[quad_col], normalize="index") * 100
        quads_hm = ["Tendu", "Actif", "Passif", "Detendu"]
        for q in quads_hm:
            if q not in ct_hm.columns:
                ct_hm[q] = 0
        ct_hm = ct_hm.sort_values("Tendu", ascending=True)
        cmaps = {"Tendu": ["#ffffff", "#e74c3c"], "Actif": ["#ffffff", "#3498db"], "Passif": ["#ffffff", "#f39c12"], "Detendu": ["#ffffff", "#2ecc71"]}
        fig_hm, axes = plt.subplots(1, 4, figsize=(20, 1 + len(ct_hm) * 0.4), sharey=True)
        fig_hm.patch.set_facecolor("#f8f9fa")
        for ax, q in zip(axes, quads_hm):
            cm = LinearSegmentedColormap.from_list(f"c_{q}", cmaps[q])
            sns.heatmap(ct_hm[[q]], ax=ax, cmap=cm, vmin=0, vmax=60,
                        annot=True, fmt=".0f", annot_kws={"size": 8},
                        linewidths=0.5, linecolor="#eee", cbar=False)
            ax.set_title(q.upper(), fontsize=11, fontweight="bold", color=cmaps[q][1])
            ax.set_xlabel("%", fontsize=9)
            ax.tick_params(axis="y", labelsize=9)
            for spine in ax.spines.values():
                spine.set_visible(False)
        plt.suptitle("Répartition Karasek par Direction — seuil théorique", fontsize=13, fontweight="bold", y=1.02)
        png_hm = fig_to_png(fig_hm)
        if png_hm:
            st.download_button("⬇ Télécharger PNG", data=png_hm, file_name="heatmap_direction.png", mime="image/png", key="k_dl_hm")
        st.pyplot(fig_hm, use_container_width=True)
        plt.close(fig_hm)


# =============================================================================
# TAB 3 — CROISEMENT
# =============================================================================
with tab_cross:
    section_title("Exploration des données démographiques")

    csp_actual = next((c for c in df.columns if re.search(r"categorie.*socio|csp", _norm(c))), "Categorie Socio")

    VAR_MAP = {
        "Genre":                          "Genre",
        "Tranche d'âge":                  "Tranche_age",
        "Ancienneté":                     "Tranche_anciennete",
        "Catégorie socioprofessionnelle":  csp_actual,
        "Catégorie IMC":                  "Categorie_IMC",
    }
    CROSS_MAP = {
        "Aucun croisement":                 None,
        "Quadrant Karasek":                 "Karasek_quadrant_theoretical",
        "Charge mentale (catég.)":          "Dem_score_theo_cat",
        "Autonomie décisionnelle (catég.)": "Lat_score_theo_cat",
        "Soutien social (catég.)":          "SS_score_theo_cat",
        "Reconnaissance (catég.)":          "rec_score_theo_cat",
        "Satisfaction (catég.)":            "sat_score_theo_cat",
        "Culture d'entreprise (catég.)":    "cult_score_theo_cat",
    }

    avail_vars  = [k for k, v in VAR_MAP.items()  if v and v in df.columns]
    avail_cross = [k for k, v in CROSS_MAP.items() if v is None or (v and v in df.columns)]

    cx1, cx2 = st.columns(2)
    with cx1:
        st.markdown('<span style="font-size:0.76rem;font-weight:700;color:#2F577F;letter-spacing:0.1em;text-transform:uppercase;">Variable à visualiser</span>', unsafe_allow_html=True)
        sel_var   = st.selectbox("Variable",    avail_vars,  key="k_cr_var",   label_visibility="collapsed")
    with cx2:
        st.markdown('<span style="font-size:0.76rem;font-weight:700;color:#2F577F;letter-spacing:0.1em;text-transform:uppercase;">Croiser avec (optionnel)</span>', unsafe_allow_html=True)
        sel_cross = st.selectbox("Croisement", avail_cross, key="k_cr_cross", label_visibility="collapsed")

    real_col  = VAR_MAP.get(sel_var)
    cross_col = CROSS_MAP.get(sel_cross)

    if real_col and real_col in df.columns:
        if cross_col and cross_col in df.columns:
            fig_cr = make_stacked(df, real_col, cross_col)
            if fig_cr:
                st.plotly_chart(fig_cr, use_container_width=True, key="k_cr_stacked")
                tmp = df[[real_col, cross_col]].dropna()
                if not tmp.empty:
                    pct_tbl = pd.crosstab(tmp[real_col].astype(str), tmp[cross_col].astype(str), normalize="index").mul(100).round(1)
                    st.markdown("**Tableau de distribution (%)**")
                    st.dataframe(pct_tbl.style.format("{:.1f}%"), use_container_width=True)
                    with st.expander("Effectifs bruts"):
                        st.dataframe(pd.crosstab(tmp[real_col].astype(str), tmp[cross_col].astype(str), margins=True, margins_name="Total"), use_container_width=True)
            else:
                st.info("Données insuffisantes pour ce croisement.")
        else:
            c_chart, c_table = st.columns([6, 4])
            with c_chart:
                fig_bar = make_barplot(df, real_col)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True, key="k_cr_bar")
            with c_table:
                cnt = df[real_col].value_counts().reset_index()
                cnt.columns = [sel_var, "N"]
                cnt["%"] = (cnt["N"] / cnt["N"].sum() * 100).round(1)
                st.dataframe(cnt, use_container_width=True, hide_index=True)
    else:
        st.info("Sélectionnez une variable pour afficher le graphique.")
