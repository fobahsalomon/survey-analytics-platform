"""
app.py — Page d'accueil SurveyLens
Hub central de navigation vers les trois questionnaires.
"""

import streamlit as st

st.set_page_config(
    page_title="SurveyLens · Bien-être au Travail",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #0F2340; }

.stApp {
    background-color: #F0F7FF;
    background-image:
        radial-gradient(ellipse 1000px 500px at 10% -5%, rgba(56,163,232,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 600px 400px at 90% 105%, rgba(249,115,22,0.08) 0%, transparent 50%);
}
.main .block-container { padding-top: 3rem; padding-left: 3rem; padding-right: 3rem; max-width: 1200px; margin: 0 auto; }

.hero { text-align: center; padding: 3rem 0 2rem; }
.hero h1 {
    font-family: 'Fraunces', Georgia, serif; font-size: 3rem; font-weight: 600;
    font-style: italic; color: #0F2340; letter-spacing: -0.02em; margin: 0; line-height: 1.1;
}
.hero h1 span { color: #38A3E8; }
.hero p { font-size: 1.1rem; color: #4E6A88; margin-top: 0.8rem; max-width: 600px; margin-left: auto; margin-right: auto; }

.module-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-top: 2.5rem; }

.module-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 20px;
    padding: 2rem 1.5rem 1.8rem; text-align: center; cursor: pointer;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 20px rgba(56,163,232,0.07);
}
.module-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: var(--accent, #38A3E8); opacity: 0; transition: opacity 0.25s;
}
.module-card:hover { transform: translateY(-6px); border-color: #AAD5F5; box-shadow: 0 16px 40px rgba(56,163,232,0.18); }
.module-card:hover::before { opacity: 1; }

.module-icon {
    width: 64px; height: 64px; border-radius: 18px; display: inline-flex;
    align-items: center; justify-content: center; margin-bottom: 1.2rem;
    font-size: 1.8rem;
}
.module-name {
    font-family: 'Fraunces', serif; font-size: 1.3rem; font-style: italic;
    font-weight: 600; color: #0F2340; margin-bottom: 0.5rem;
}
.module-desc { font-size: 0.88rem; color: #4E6A88; line-height: 1.6; }
.module-tag {
    display: inline-block; margin-top: 1rem; font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.08em; text-transform: uppercase; padding: 0.25rem 0.9rem;
    border-radius: 999px; background: var(--tag-bg, #EDF5FD); color: var(--tag-color, #38A3E8);
}

.stButton > button {
    background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important;
    border: none !important; color: #FFFFFF !important; border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 0.9rem !important; padding: 0.65rem 2rem !important;
    box-shadow: 0 3px 12px rgba(56,163,232,0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #F97316, #EA6A0A) !important;
    box-shadow: 0 6px 20px rgba(249,115,22,0.35) !important;
    transform: translateY(-2px) !important;
}

.footer {
    text-align: center; margin-top: 3rem; padding: 1.5rem;
    font-size: 0.78rem; color: #94A3B8; border-top: 1px solid #E4F0FB;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<div class="hero">
    <h1>Survey<span>-Lens</span></h1>
    <p>Plateforme d'analyse des risques psychosociaux et du bien-être au travail</p>
</div>

<div class="module-grid">

<div class="module-card" style="--accent:#EF4444;">
    <div class="module-icon" style="background:rgba(239,68,68,0.1);">🧠</div>
    <div class="module-name">Karasek DCS</div>
    <div class="module-desc">
    Modèle Demande–Contrôle–Soutien. Analyse du Job Strain, Iso-Strain
    et des quadrants psychosociaux selon Karasek & Theorell.
    </div>
    <span class="module-tag" style="--tag-bg:rgba(239,68,68,0.08);--tag-color:#DC2626;">RPS · Stress</span>
</div>

<div class="module-card" style="--accent:#22C55E;">
    <div class="module-icon" style="background:rgba(34,197,94,0.1);">🌱</div>
    <div class="module-name">QVT</div>
    <div class="module-desc">
    Qualité de Vie au Travail selon le cadre ANACT / ANI 2013.
    Évalue 6 dimensions clés du bien-être organisationnel.
    </div>
    <span class="module-tag" style="--tag-bg:rgba(34,197,94,0.08);--tag-color:#15803D;">QVT · Bien-être</span>
</div>

<div class="module-card" style="--accent:#F97316;">
    <div class="module-icon" style="background:rgba(249,115,22,0.1);">🔥</div>
    <div class="module-name">MBI Burnout</div>
    <div class="module-desc">
    Maslach Burnout Inventory — General Survey (MBI-GS).
    Mesure l'épuisement, le cynisme et l'efficacité personnelle.
    </div>
    <span class="module-tag" style="--tag-bg:rgba(249,115,22,0.08);--tag-color:#C2410C;">Burnout · MBI-GS</span>
</div>

</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Ouvrir Karasek DCS →", key="nav_karasek", use_container_width=True):
        st.switch_page("pages/1_karasek.py")
with col2:
    if st.button("Ouvrir QVT →", key="nav_qvt", use_container_width=True):
        st.switch_page("pages/2_qvt.py")
with col3:
    if st.button("Ouvrir MBI Burnout →", key="nav_mbi", use_container_width=True):
        st.switch_page("pages/3_mbi.py")

st.markdown("""
<div class="footer">
    SurveyLens · Plateforme d'analyse psychosociale · indicateurs conventionnels
</div>
""", unsafe_allow_html=True)
