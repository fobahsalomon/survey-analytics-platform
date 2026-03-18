"""
pages/_ui_shared.py
Composants UI Streamlit partagés entre toutes les pages du dashboard.
"""

import io
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


# =============================================================================
# CSS GLOBAL — palette Wave-CI
# =============================================================================
def inject_css():
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
.main .block-container { padding-top: 0.75rem; padding-left: 2rem; padding-right: 2rem; max-width: 1500px; }

[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #D0E8F8 !important; }

.hero-band {
    background: linear-gradient(135deg, #FFFFFF 0%, #F5F9FF 100%);
    border: 1px solid #D0E8F8; border-radius: 20px; padding: 1.4rem 2rem 1.3rem;
    margin-bottom: 0.9rem; position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(56,163,232,0.08), 0 1px 0 rgba(255,255,255,0.9) inset;
}
.hero-band::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #38A3E8, #F97316, #38A3E8);
    background-size: 200% 100%; animation: shimmer 4s linear infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

.section-title {
    display: flex; align-items: center; gap: 0.7rem; font-family: 'Fraunces', serif;
    font-size: 1.2rem; font-style: italic; font-weight: 400; color: #0F2340;
    margin: 1.8rem 0 1rem; padding-bottom: 0.65rem; border-bottom: 2px solid #E4F0FB;
}
.section-title::before {
    content: ''; display: inline-block; width: 4px; height: 20px;
    background: linear-gradient(180deg, #38A3E8 0%, #F97316 100%); border-radius: 2px; flex-shrink: 0;
}

.kpi-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 16px;
    padding: 1.3rem 1.2rem 1.1rem; text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06); position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #38A3E8, #F97316); opacity: 0; transition: opacity 0.22s;
}
.kpi-card:hover { transform: translateY(-4px); border-color: #AAD5F5; box-shadow: 0 10px 32px rgba(56,163,232,0.15); }
.kpi-card:hover::after { opacity: 1; }
.kpi-label { font-size: 0.8rem; color: #4E6A88 !important; text-transform: uppercase; letter-spacing: 0.09em; font-weight: 700; margin-bottom: 0.55rem; display: block; }
.kpi-icon { width: 38px; height: 38px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.55rem; }
.kpi-value { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.35rem; font-weight: 800; color: #0F2340 !important; line-height: 1; letter-spacing: -0.04em; }
@keyframes slideUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }

.gauge-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 18px;
    padding: 1.6rem 1.2rem 1.3rem; text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06); height: 100%; position: relative; overflow: hidden;
}
.gauge-card:hover { transform: translateY(-4px); border-color: #AAD5F5; box-shadow: 0 12px 36px rgba(56,163,232,0.15); }
.gauge-semi-wrap { position: relative; width: 180px; height: 90px; margin: 0 auto 0.7rem; overflow: hidden; }
.gauge-semi-bg   { position: absolute; width: 180px; height: 180px; border-radius: 50%; background: #EDF5FD; top: 0; left: 0; }
.gauge-semi-fill {
    position: absolute; width: 180px; height: 180px; border-radius: 50%; top: 0; left: 0;
    background: conic-gradient(from 270deg, var(--gauge-color,#38A3E8) 0deg, var(--gauge-color,#38A3E8) calc(var(--g,0deg)), transparent calc(var(--g,0deg)));
}
.gauge-semi-inner { position: absolute; width: 112px; height: 112px; background: #FFFFFF; border-radius: 50%; top: 34px; left: 34px; box-shadow: inset 0 2px 8px rgba(56,163,232,0.06); }
.gauge-value    { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.9rem; font-weight: 800; color: #0F2340; line-height: 1; letter-spacing: -0.04em; }
.gauge-pct      { font-size: 1rem; font-weight: 500; color: #6B88A8; }
.gauge-label    { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.96rem; font-weight: 700; color: #0F2340; margin-top: 0.55rem; }
.gauge-sublabel { font-size: 0.84rem; color: #4E6A88; margin-top: 0.25rem; line-height: 1.5; }
.gauge-badge    { display: inline-block; margin-top: 0.7rem; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; padding: 0.22rem 0.85rem; border-radius: 999px; }
.gauge-badge.good  { background: #DCFCE7; color: #15803D; }
.gauge-badge.alert { background: #FEE2E2; color: #B91C1C; }
.gauge-badge.warn  { background: #FEF3C7; color: #92400E; }

.prog-track { background: #EDF5FD; border-radius: 999px; height: 7px; overflow: hidden; margin-top: 5px; }
.prog-fill  { height: 7px; border-radius: 999px; width: 0%; transition: width 1.1s cubic-bezier(0.4,0,0.2,1); }
.panel-relief { background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 16px; padding: 0.9rem 1rem 0.6rem; box-shadow: 0 3px 14px rgba(56,163,232,0.08); }

.workzone-card, .ls-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 14px;
    padding: 1.1rem 1rem; text-align: center; transition: transform 0.2s, box-shadow 0.2s;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 6px rgba(56,163,232,0.05);
}
.workzone-card:hover, .ls-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(56,163,232,0.12); }

[data-baseweb="tab-list"] { background: #FFFFFF !important; border-radius: 12px; padding: 4px; gap: 3px; border: 1px solid #D0E8F8; box-shadow: 0 2px 8px rgba(56,163,232,0.07); }
[data-baseweb="tab"] { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.88rem !important; color: #6B88A8 !important; border-radius: 9px !important; padding: 0.5rem 1.4rem !important; transition: all 0.2s !important; }
[aria-selected="true"][data-baseweb="tab"] { background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important; color: #FFFFFF !important; font-weight: 700 !important; box-shadow: 0 3px 12px rgba(56,163,232,0.3) !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

[data-baseweb="select"] > div { background-color: #FFFFFF !important; border-color: #C8DFF2 !important; border-radius: 10px !important; color: #0F2340 !important; }
.stButton > button { background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important; border: none !important; color: #FFFFFF !important; border-radius: 10px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; font-size: 0.8rem !important; letter-spacing: 0.02em !important; box-shadow: 0 3px 10px rgba(56,163,232,0.25) !important; transition: all 0.18s !important; }
.stButton > button:hover { background: linear-gradient(135deg, #F97316, #EA6A0A) !important; box-shadow: 0 4px 16px rgba(249,115,22,0.3) !important; transform: translateY(-1px) !important; }

div[data-testid="stPlotlyChart"] { border: 1px solid #D6E8F7; border-radius: 12px; background: #FFFFFF; box-shadow: 0 4px 16px rgba(56,163,232,0.06); padding: 4px; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #EDF5FD; }
::-webkit-scrollbar-thumb { background: #AAD5F5; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38A3E8; }

hr { border: none; border-top: 1px solid #E4F0FB; margin: 1rem 0; }
@property --g { syntax: '<angle>'; inherits: false; initial-value: 0deg; }

/* Export button special style */
.export-btn { margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)


def inject_animation_js():
    components.html("""
<script>
const rootDoc = window.parent && window.parent.document ? window.parent.document : document;
function easeOut(t) { return 1 - Math.pow(1-t,3); }
function cleanNum(v,min,max){var n=parseFloat(v);if(!isFinite(n))n=0;if(typeof min==='number')n=Math.max(min,n);if(typeof max==='number')n=Math.min(max,n);return n;}
function isVisible(el){if(!el||!el.isConnected)return false;const s=rootDoc.defaultView.getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden'||s.opacity==='0')return false;const r=el.getBoundingClientRect();return r.width>0&&r.height>0;}
function numberKey(el){return[cleanNum(el.dataset.target,0,null),el.dataset.suffix||'',el.dataset.prefix||'',el.dataset.decimals||0].join('|');}
function animateNumber(el){
    const target=cleanNum(el.dataset.target,0,null),suffix=el.dataset.suffix||'',prefix=el.dataset.prefix||'',decimals=el.dataset.decimals?parseInt(el.dataset.decimals,10):0,key=numberKey(el);
    if(el.dataset.animKey===key)return;el.dataset.animKey=key;
    const duration=700,start=performance.now();
    (function step(now){const t=Math.min(1,(now-start)/duration),cur=Math.max(0,target*easeOut(t));
    el.textContent=prefix+(decimals===0?Math.round(cur):cur.toFixed(decimals))+suffix;
    if(t<1)requestAnimationFrame(step);else el.textContent=prefix+(decimals===0?Math.round(target):target.toFixed(decimals))+suffix;})(start);
}
function animateGauge(fill){
    const target=cleanNum(fill.dataset.target,0,100),key=String(target);
    if(fill.dataset.animKey===key)return;fill.dataset.animKey=key;
    const counter=fill.closest('.gauge-card')?.querySelector('.gauge-counter'),duration=800,start=performance.now();
    fill.style.setProperty('--g','0deg');
    requestAnimationFrame(()=>setTimeout(()=>fill.style.setProperty('--g',(target*1.8).toFixed(1)+'deg'),60));
    if(counter){(function step(now){const t=Math.min(1,(now-start)/duration);counter.textContent=Math.round(target*easeOut(t));if(t<1)requestAnimationFrame(step);else counter.textContent=Math.round(target);})(start);}
}
function animateProgress(el){
    const target=cleanNum(el.dataset.target,0,100),key=String(target);
    if(el.dataset.animKey===key)return;el.dataset.animKey=key;
    el.style.width='0%';requestAnimationFrame(()=>setTimeout(()=>el.style.width=target+'%',40));
}
function runFor(el){if(el.matches('.animate-number'))animateNumber(el);else if(el.matches('.gauge-semi-fill[data-target]'))animateGauge(el);else if(el.matches('.prog-fill[data-target]'))animateProgress(el);}
const observed=new WeakSet(),io=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting&&isVisible(e.target))runFor(e.target);});},{threshold:0.2});
function register(){
    rootDoc.querySelectorAll('.animate-number,.gauge-semi-fill[data-target],.prog-fill[data-target]').forEach(el=>{
        if(el.matches('.animate-number')){const k=numberKey(el);if(el.dataset.animKey&&el.dataset.animKey!==k)delete el.dataset.animKey;}
        else{const t=cleanNum(el.dataset.target,0,100);if(el.dataset.animKey&&el.dataset.animKey!==String(t))delete el.dataset.animKey;}
        if(!observed.has(el)){io.observe(el);observed.add(el);}
        if(isVisible(el)){const r=el.getBoundingClientRect(),vh=rootDoc.defaultView?.innerHeight||900;if(r.top<vh*0.92&&r.bottom>0)runFor(el);}
    });
}
setTimeout(register,60);
let _t=null;new MutationObserver(()=>{if(_t)clearTimeout(_t);_t=setTimeout(()=>setTimeout(register,60),90);}).observe(rootDoc.body,{childList:true,subtree:true});
rootDoc.addEventListener('click',evt=>{if(evt.target?.closest('[role="tab"]'))setTimeout(()=>setTimeout(register,60),120);},true);
</script>
""", height=0)


# =============================================================================
# HTML COMPONENTS
# =============================================================================

def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def svg_icon(path_d: str, bg: str, fg: str) -> str:
    return (f'<span class="kpi-icon" style="background:{bg};color:{fg};">'
            f'<svg viewBox="0 0 24 24" width="17" height="17" fill="none">'
            f'<path d="{path_d}" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'</svg></span>')


def html_kpi(value, label, suffix="", prefix="", decimals=0, subtitle="", icon="") -> str:
    num = float(pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0] or 0)
    rend = f"{num:.{decimals}f}" if decimals > 0 else str(int(round(num)))
    sub  = f'<div style="margin-top:0.4rem;font-size:0.78rem;font-weight:600;color:#4E6A88;">{subtitle}</div>' if subtitle else ""
    ico  = icon if str(icon).strip().startswith("<") else ""
    return f"""<div class="kpi-card">{ico}<span class="kpi-label">{label}</span>
    <div class="kpi-value animate-number" data-target="{num}" data-suffix="{suffix}" data-prefix="{prefix}" data-decimals="{decimals}">{prefix}{rend}{suffix}</div>{sub}</div>"""


def html_gauge(value, label, sublabel, inverted=False) -> str:
    t = max(0.0, min(100.0, float(value) if not pd.isna(value) else 0.0))
    d = int(round(t))
    if inverted:
        col, bcls, btxt = ("#EF4444", "alert", "Élevée") if t > 50 else ("#22C55E", "good", "Modérée")
    else:
        col, bcls, btxt = ("#22C55E", "good", "Élevé") if t > 50 else ("#EF4444", "alert", "Faible")
    return f"""<div class="gauge-card">
    <div class="gauge-semi-wrap">
        <div class="gauge-semi-bg"></div>
        <div class="gauge-semi-fill" style="--gauge-color:{col};--g:{t*1.8:.1f}deg;" data-target="{d}"></div>
        <div class="gauge-semi-inner"></div>
    </div>
    <div class="gauge-value"><span class="gauge-counter" style="color:{col};">{d}</span><span class="gauge-pct">%</span></div>
    <div class="gauge-label">{label}</div><div class="gauge-sublabel">{sublabel}</div>
    <span class="gauge-badge {bcls}">{btxt}</span></div>"""


def html_gauge_raw(value, max_value, label, sublabel, color="#38A3E8", badge_text="") -> str:
    """Jauge avec valeur brute (non %) — pour MBI (échelle 0-6) et QVT."""
    pct = max(0.0, min(100.0, float(value) / max_value * 100 if max_value else 0))
    d   = round(float(value), 1) if not pd.isna(value) else 0
    return f"""<div class="gauge-card">
    <div class="gauge-semi-wrap">
        <div class="gauge-semi-bg"></div>
        <div class="gauge-semi-fill" style="--gauge-color:{color};--g:{pct*1.8:.1f}deg;" data-target="{int(pct)}"></div>
        <div class="gauge-semi-inner"></div>
    </div>
    <div class="gauge-value" style="color:{color};font-size:1.6rem;">{d}</div>
    <div class="gauge-label">{label}</div><div class="gauge-sublabel">{sublabel}</div>
    {"<span class='gauge-badge good'>" + badge_text + "</span>" if badge_text else ""}</div>"""


def html_prog(label, pct, color, n=0) -> str:
    v = max(0.0, min(100.0, float(pct) if not pd.isna(pct) else 0.0))
    return f"""<div style="margin-bottom:1rem;">
    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-size:0.78rem;color:#3B5878;font-family:'Plus Jakarta Sans',sans-serif;font-weight:500;">{label}</span>
        <span style="font-size:0.82rem;font-weight:700;color:{color};font-family:'Plus Jakarta Sans',sans-serif;">{v:.0f}% ({int(n)})</span>
    </div>
    <div class="prog-track"><div class="prog-fill" style="background:{color};width:{v:.1f}%;" data-target="{v:.1f}"></div></div></div>"""


def html_zone(label, pct, n, color) -> str:
    v = max(0.0, min(100.0, float(pct) if not pd.isna(pct) else 0.0))
    return f"""<div class="workzone-card" style="border-top:3px solid {color};">
    <span class="kpi-label">{label}</span>
    <div class="kpi-value animate-number" style="color:{color};font-size:1.8rem;" data-target="{int(round(v))}" data-suffix="%" data-prefix="" data-decimals="0">{int(round(v))}%</div>
    <div style="margin-top:0.35rem;font-size:0.78rem;font-weight:600;color:#4E6A88;">{int(n)}</div></div>"""


def html_ls_n(pct, n, label) -> str:
    num = float(pct) if not pd.isna(pct) else 0.0
    col = "#22C55E" if num < 35 else "#EF4444" if num > 60 else "#F97316"
    return f"""<div class="ls-card" style="border-top:3px solid {col};">
    <span class="kpi-label">{label}</span>
    <div class="kpi-value animate-number" style="color:{col};font-size:1.8rem;" data-target="{int(round(num))}" data-suffix="%" data-prefix="" data-decimals="0">{int(round(num))}%</div>
    <div style="margin-top:0.3rem;font-size:0.78rem;font-weight:600;color:#4E6A88;">n = {int(n)}</div></div>"""


# =============================================================================
# PLOTLY HELPERS
# =============================================================================

def _plotly_base(fig, height=None):
    upd = dict(
        plot_bgcolor="#FAFCFF", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#0F2340", size=12),
        xaxis=dict(showgrid=True, gridcolor="#EDF5FD", gridwidth=1, showline=True,
                   linecolor="#D6E8F7", zeroline=False, tickfont=dict(color="#6B88A8", size=11)),
        yaxis=dict(showgrid=True, gridcolor="#EDF5FD", gridwidth=1, showline=False,
                   zeroline=False, tickfont=dict(color="#6B88A8", size=11)),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#D6E8F7", borderwidth=1,
                    font=dict(color="#0F2340", size=11)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    if height:
        upd["height"] = height
    fig.update_layout(**upd)
    return fig


def make_barplot(df, col):
    cnt = df[col].value_counts().reset_index()
    cnt.columns = [col, "n"]
    cnt["pct"] = (cnt["n"] / cnt["n"].sum() * 100).round(1)
    pal = ["#38A3E8", "#F97316", "#22C55E", "#EF4444", "#A78BFA", "#06B6D4", "#FB923C", "#84CC16"]
    fig = go.Figure()
    for i, row in cnt.iterrows():
        fig.add_trace(go.Bar(
            y=[row[col]], x=[row["pct"]], orientation="h",
            marker_color=pal[i % len(pal)],
            marker=dict(opacity=0.9, line=dict(width=0)),
            text=f"{row['pct']}%  ({row['n']})", textposition="outside",
            textfont=dict(color="#6B88A8", size=11, family="Plus Jakarta Sans"),
            showlegend=False,
        ))
    _plotly_base(fig, height=max(250, len(cnt) * 55 + 80))
    fig.update_xaxes(range=[0, 130], title_text="Pourcentage (%)")
    return fig


def make_stacked(df, x_col, hue_col):
    if x_col not in df.columns or hue_col not in df.columns:
        return None
    tmp = df[[x_col, hue_col]].dropna()
    if tmp.empty:
        return None
    ct  = pd.crosstab(tmp[x_col], tmp[hue_col])
    pct = ct.div(ct.sum(axis=1), axis=0) * 100
    KARASEK_COLORS = {"Actif": "#22C55E", "Détendu": "#38A3E8", "Detendu": "#38A3E8", "Tendu": "#EF4444", "Passif": "#94A3B8"}
    bmap = {"Eleve": "#22C55E", "Élevé": "#22C55E", "Faible": "#EF4444", "Présent": "#EF4444", "Absent": "#22C55E",
            "Satisfaisant": "#22C55E", "Mitigé": "#F97316", "Insatisfaisant": "#EF4444",
            "Bas": "#22C55E", "Modéré": "#F97316"}
    gen = ["#38A3E8", "#F97316", "#22C55E", "#EF4444", "#A78BFA", "#06B6D4"]
    def gc(cat, idx):
        if cat in KARASEK_COLORS: return KARASEK_COLORS[cat]
        if cat in bmap: return bmap[cat]
        return gen[idx % len(gen)]
    fig = go.Figure()
    for i, cat in enumerate(pct.columns):
        vals, ns = pct[cat].values, ct[cat].values
        txts = [f"{v:.1f}%  ({n})" if v >= 6 else "" for v, n in zip(vals, ns)]
        fig.add_trace(go.Bar(
            name=str(cat), y=list(pct.index), x=vals, orientation="h",
            marker_color=gc(str(cat), i),
            marker=dict(opacity=0.9, line=dict(width=0)),
            text=txts, textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=11, family="Plus Jakarta Sans"),
        ))
    _plotly_base(fig, height=max(280, len(pct.index) * 55 + 100))
    fig.update_layout(barmode="stack", xaxis=dict(range=[0, 100], title_text="Pourcentage (%)"))
    return fig


def make_radar(scores: dict, labels: list):
    vals = [scores.get(l, 0) for l in labels]
    vc = vals + [vals[0]]
    lc = labels + [labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[50] * (len(labels) + 1), theta=lc, fill="toself",
        fillcolor="rgba(249,115,22,0.05)",
        line=dict(color="rgba(249,115,22,0.4)", dash="dot", width=1.5),
        name="Référence 50%", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=vc, theta=lc, fill="toself",
        fillcolor="rgba(56,163,232,0.12)",
        line=dict(color="#38A3E8", width=2.5),
        marker=dict(color="#38A3E8", size=7, line=dict(color="#FFFFFF", width=2)),
        name="Niveau élevé",
        hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#FAFCFF",
            angularaxis=dict(tickfont=dict(color="#0F2340", size=10, family="Plus Jakarta Sans"), linecolor="#D6E8F7", gridcolor="#EDF5FD"),
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#6B88A8", size=9), gridcolor="#EDF5FD", linecolor="#D6E8F7", ticksuffix="%"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#0F2340"),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#D6E8F7", borderwidth=1, font=dict(color="#0F2340", size=11), x=0.75, y=1.1),
        height=500, margin=dict(l=60, r=60, t=40, b=40),
    )
    return fig


def fig_to_png(fig) -> bytes | None:
    try:
        if hasattr(fig, "to_image"):
            return fig.to_image(format="png")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        return buf.read()
    except Exception:
        return None


# =============================================================================
# SIDEBAR FILTRES COMMUN
# =============================================================================

def _norm(v):
    return re.sub(r"\s+", " ", str(v).strip()).casefold()


def _clean_opts(series):
    out = {}
    for raw in series.dropna().astype(str):
        c = re.sub(r"\s+", " ", raw.strip())
        if c:
            out.setdefault(_norm(c), c)
    return sorted(out.values(), key=_norm)


def render_sidebar(df_raw: pd.DataFrame, prefix: str = "sb") -> pd.DataFrame:
    """
    Affiche les filtres dans la sidebar et retourne le DataFrame filtré.
    prefix : préfixe unique par page pour éviter les conflits de clés session_state.
    """
    with st.sidebar:
        st.markdown("""
        <div style="font-family:'Fraunces',serif;font-size:1.15rem;font-style:italic;
                    color:#0F2340;font-weight:400;margin-bottom:1.2rem;padding-bottom:0.6rem;
                    border-bottom:2px solid #E4F0FB;">Filtres</div>""", unsafe_allow_html=True)

        ALL = "Tous"

        dirs = [ALL] + (_clean_opts(df_raw["Direction"]) if "Direction" in df_raw.columns else [])
        if st.session_state.get(f"{prefix}_dir") not in dirs:
            st.session_state[f"{prefix}_dir"] = ALL
        sel_dir = st.selectbox("Direction", dirs, key=f"{prefix}_dir")

        dep = df_raw
        if "Direction" in df_raw.columns and sel_dir != ALL:
            mask = df_raw["Direction"].astype(str).map(_norm) == _norm(sel_dir)
            dep = df_raw[mask]

        # CSP
        csp_c = next((c for c in df_raw.columns if re.search(r"categorie.*socio|csp", _norm(c))), None)
        csps = [ALL] + (_clean_opts(dep[csp_c]) if csp_c else [])
        if st.session_state.get(f"{prefix}_csp") not in csps:
            st.session_state[f"{prefix}_csp"] = ALL
        sel_csp = st.selectbox("Catégorie socio", csps, key=f"{prefix}_csp")

        genres = [ALL] + (_clean_opts(dep["Genre"]) if "Genre" in dep.columns else [])
        if st.session_state.get(f"{prefix}_genre") not in genres:
            st.session_state[f"{prefix}_genre"] = ALL
        sel_genre = st.selectbox("Genre", genres, key=f"{prefix}_genre")

        age_s = pd.to_numeric(df_raw["Age"], errors="coerce").dropna() if "Age" in df_raw.columns else pd.Series(dtype=float)
        sel_age = None
        if not age_s.empty:
            ab = (int(np.floor(age_s.min())), int(np.ceil(age_s.max())))
            cur = st.session_state.get(f"{prefix}_age", ab)
            if not isinstance(cur, tuple):
                cur = ab
            safe_val = (max(ab[0], int(cur[0])), min(ab[1], int(cur[1])))
            sel_age = st.slider("Tranche d'âge", min_value=ab[0], max_value=ab[1], value=safe_val, key=f"{prefix}_age")

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("↺ Réinitialiser", key=f"{prefix}_reset", use_container_width=True):
            for k in [f"{prefix}_dir", f"{prefix}_csp", f"{prefix}_genre", f"{prefix}_age"]:
                st.session_state.pop(k, None)
            st.rerun()

    # Application des filtres
    out = df_raw.copy()
    if "Direction" in out.columns and sel_dir != ALL:
        mask = out["Direction"].astype(str).map(_norm) == _norm(sel_dir)
        out = out[mask]
    if csp_c and sel_csp != ALL:
        out = out[out[csp_c].astype(str).map(_norm) == _norm(sel_csp)]
    if "Genre" in out.columns and sel_genre != ALL:
        out = out[out["Genre"].astype(str).map(_norm) == _norm(sel_genre)]
    if sel_age and "Age" in out.columns:
        ages = pd.to_numeric(out["Age"], errors="coerce")
        out = out[(ages >= sel_age[0]) & (ages <= sel_age[1])]
    return out


# =============================================================================
# EXPORT WORD BUTTON
# =============================================================================

def render_export_button(report_bytes: bytes, filename: str, label: str = "📄 Exporter le rapport Word"):
    """Bouton de téléchargement du rapport Word."""
    st.download_button(
        label=label,
        data=report_bytes,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )
