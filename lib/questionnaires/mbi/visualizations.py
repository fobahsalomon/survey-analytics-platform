"""
lib/questionnaires/mbi/visualizations.py
Visualisations MBI — retourne des bytes PNG.
"""

import io, textwrap, warnings
from typing import Dict, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")
from .config import DIMENSIONS

ACCENT="#38A3E8"; ORANGE="#F97316"; GREEN="#22C55E"; RED="#EF4444"
DARK="#0F2340"; BG="#FAFCFF"; GRID_C="#EDF5FD"; TEXT_MID="#4E6A88"
DIM_COLORS={"exhaustion":RED,"cynicism":ORANGE,"efficacy":GREEN}
CAT_COLORS={"Bas":GREEN,"Modéré":ORANGE,"Élevé":RED}
RISK_COLORS={"Faible":GREEN,"Modéré":ORANGE,"Élevé":RED}
HOMME_C="#4472C4"; FEMME_C="#E91E8C"

def _fig_bytes(fig):
    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor=fig.get_facecolor())
    plt.close(fig); buf.seek(0); return buf.read()

def _base(ax,title="",xlabel="",ylabel="",wrap=58):
    ax.set_facecolor(BG); ax.figure.patch.set_facecolor("white")
    ax.grid(True,color=GRID_C,linewidth=0.8,axis="x",zorder=0); ax.set_axisbelow(True)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color("#D6E8F7")
    ax.tick_params(colors=TEXT_MID,labelsize=9)
    if title: ax.set_title("\n".join(textwrap.wrap(title,wrap)),fontsize=13,fontweight="bold",color=DARK,pad=14)
    if xlabel: ax.set_xlabel(xlabel,fontsize=10,color=TEXT_MID,labelpad=8)
    if ylabel: ax.set_ylabel("\n".join(textwrap.wrap(ylabel,22)),fontsize=10,color=TEXT_MID,labelpad=8)


# ── 1. RADAR MBI ──────────────────────────────────────────────────────────────

def plot_mbi_radar(df, metrics, company=""):
    """Radar des 3 dimensions MBI (% niveau élevé)."""
    dims=metrics.get("dimensions",{})
    if not dims or len(dims)<3: return None
    labels=[d["label"] for d in dims.values()]
    # % élevé — pour efficacy, on prend % Bas (= risque)
    vals=[]
    for dim_key, data in dims.items():
        cats=data.get("categories",{})
        if dim_key=="efficacy":
            vals.append(cats.get("Bas",{}).get("pct",0))  # Bas efficacy = risque
        else:
            vals.append(cats.get("Élevé",{}).get("pct",0))

    N=len(labels); angles=np.linspace(0,2*np.pi,N,endpoint=False).tolist()
    vc=vals+[vals[0]]; ac=angles+[angles[0]]
    fig,ax=plt.subplots(figsize=(7,7),subplot_kw={"polar":True})
    fig.patch.set_facecolor("white"); ax.set_facecolor(BG)
    # Zone de danger (> 30%)
    ax.plot(ac,[30]*(N+1),color=ORANGE,linestyle="--",linewidth=1.2,alpha=0.5)
    ax.fill(angles,[30]*N,color=ORANGE,alpha=0.03)
    ax.plot(ac,[60]*(N+1),color=RED,linestyle=":",linewidth=1.0,alpha=0.35)

    ax.plot(ac,vc,color=RED,linewidth=2.3,zorder=3)
    ax.fill(angles,vals,color=RED,alpha=0.12,zorder=2)
    ax.scatter(angles,vals,color=RED,s=55,zorder=4,edgecolors="white",linewidths=1.5)
    for a,v in zip(angles,vals):
        ax.annotate(f"{v:.0f}%",xy=(a,v),xytext=(a,v+8),
                    ha="center",va="center",fontsize=9,fontweight="bold",color=DARK)

    ax.set_xticks(angles)
    ax.set_xticklabels(["\n".join(textwrap.wrap(l,13)) for l in labels],fontsize=9,color=DARK)
    ax.set_ylim(0,100); ax.set_yticks([25,50,75,100])
    ax.set_yticklabels(["25%","50%","75%","100%"],fontsize=7,color=TEXT_MID)
    ax.yaxis.grid(True,color=GRID_C,linewidth=0.8); ax.xaxis.grid(True,color=GRID_C,linewidth=0.8)
    ax.spines["polar"].set_color("#D6E8F7")
    suffix=f" — {company}" if company else ""
    ax.set_title(f"Radar MBI-GS{suffix}\n(% à risque par dimension)",
                 fontsize=11,fontweight="bold",color=DARK,pad=22)
    handles=[
        mpatches.Patch(color=RED,alpha=0.6,label="% à risque élevé"),
        plt.Line2D([0],[0],color=ORANGE,linestyle="--",linewidth=1.2,label="Seuil vigilance 30%"),
    ]
    ax.legend(handles=handles,loc="lower right",bbox_to_anchor=(1.35,-0.05),fontsize=8,framealpha=0.9)
    fig.tight_layout(); return _fig_bytes(fig)


# ── 2. BARRES COMPARATIVES DIMENSIONS ─────────────────────────────────────────

def plot_mbi_bars(df, metrics, company=""):
    """Barres groupées Bas/Modéré/Élevé par dimension MBI."""
    dims=metrics.get("dimensions",{})
    if not dims: return None
    dim_labels=[d["label"] for d in dims.values()]
    cats=["Bas","Modéré","Élevé"]
    x=np.arange(len(dim_labels)); width=0.26
    fig,ax=plt.subplots(figsize=(10,5))
    for i,cat in enumerate(cats):
        vals=[d.get("categories",{}).get(cat,{}).get("pct",0) for d in dims.values()]
        bars=ax.bar(x+i*width,vals,width,label=cat,color=CAT_COLORS[cat],
                    edgecolor="white",alpha=0.9,zorder=3)
        for bar,v in zip(bars,vals):
            if v>=5:
                ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1.5,
                        f"{v:.0f}%",ha="center",va="bottom",fontsize=8,
                        fontweight="bold",color=DARK)
    ax.set_xticks(x+width)
    ax.set_xticklabels(["\n".join(textwrap.wrap(l,16)) for l in dim_labels],fontsize=9,color=DARK)
    ax.set_ylim(0,115)
    suffix=f" — {company}" if company else ""
    _base(ax,title=f"Répartition MBI par dimension{suffix}",ylabel="Pourcentage (%)")
    ax.grid(True,color=GRID_C,linewidth=0.8,axis="y",zorder=0)
    # Ligne de vigilance 30%
    ax.axhline(30,color=ORANGE,linestyle="--",linewidth=1.2,alpha=0.6,zorder=2)
    ax.text(ax.get_xlim()[1]*0.98,31,"30% (vigilance)",ha="right",
            fontsize=7,color=ORANGE)
    ax.legend(title="Niveau",fontsize=9,title_fontsize=9,framealpha=0.9)
    fig.tight_layout(); return _fig_bytes(fig)


# ── 3. JAUGES DE RISQUE BURNOUT ────────────────────────────────────────────────

def plot_burnout_risk(df, metrics, company=""):
    """Donut chart du risque burnout composite."""
    risk=metrics.get("burnout_risk",{})
    if not risk: return None
    levels=["Faible","Modéré","Élevé"]
    vals=[risk.get(l,{}).get("pct",0) for l in levels]
    ns  =[risk.get(l,{}).get("n",0)   for l in levels]
    colors=[RISK_COLORS[l] for l in levels]
    vals_nonzero=[v for v in vals if v>0]
    if not vals_nonzero: return None

    fig,ax=plt.subplots(figsize=(7,5.5))
    fig.patch.set_facecolor("white")
    wedges,texts,autotexts=ax.pie(
        vals, labels=None, colors=colors, autopct="%1.1f%%",
        startangle=90, pctdistance=0.72,
        wedgeprops={"edgecolor":"white","linewidth":2,"width":0.55},
    )
    for at in autotexts:
        at.set_fontsize(11); at.set_fontweight("bold"); at.set_color("white")

    # Centre
    total=int(sum(ns))
    ax.text(0,0.12,str(total),ha="center",va="center",
            fontsize=22,fontweight="bold",color=DARK)
    ax.text(0,-0.18,"répondants",ha="center",va="center",
            fontsize=9,color=TEXT_MID)

    legend_labels=[f"{l}  —  {v:.1f}%  (n={n})"
                   for l,v,n in zip(levels,vals,ns)]
    ax.legend(wedges,legend_labels,loc="lower center",
              bbox_to_anchor=(0.5,-0.12),fontsize=9,framealpha=0.9,
              ncol=3)
    suffix=f" — {company}" if company else ""
    ax.set_title(f"Risque burnout composite{suffix}",
                 fontsize=13,fontweight="bold",color=DARK,pad=18)
    fig.tight_layout(); return _fig_bytes(fig)


# ── 4. SCORES MOYENS PAR DIRECTION ────────────────────────────────────────────

def plot_mbi_heatmap(df, company=""):
    """Heatmap scores MBI moyens par direction."""
    dir_col=next((c for c in df.columns if c.strip().lower()=="direction"),None)
    dim_cols=[f"{d}_score" for d in DIMENSIONS if f"{d}_score" in df.columns]
    if not dir_col or not dim_cols: return None
    pivot=df.groupby(dir_col)[dim_cols].mean().round(2)
    if pivot.empty: return None
    rename={f"{d}_score":DIMENSIONS[d] for d in DIMENSIONS if f"{d}_score" in pivot.columns}
    pivot.rename(columns=rename,inplace=True)
    fig_h=max(3.5,0.5*len(pivot)+1.5)
    fig,ax=plt.subplots(figsize=(9,fig_h)); fig.patch.set_facecolor("white")
    cmap=sns.diverging_palette(140,10,s=70,l=55,as_cmap=True)  # vert→rouge
    sns.heatmap(pivot,ax=ax,cmap=cmap,vmin=0,vmax=6,annot=True,fmt=".1f",
                annot_kws={"size":9,"weight":"bold"},linewidths=0.5,
                linecolor="#F0F7FF",cbar_kws={"label":"Score moyen (0–6)"})
    suffix=f" — {company}" if company else ""
    ax.set_title(f"Scores MBI moyens par Direction{suffix}",
                 fontsize=12,fontweight="bold",color=DARK,pad=12)
    ax.set_xlabel("Dimension MBI",fontsize=10,color=TEXT_MID)
    ax.set_ylabel("Direction",fontsize=10,color=TEXT_MID)
    ax.tick_params(axis="x",labelsize=8,rotation=20,colors=TEXT_MID)
    ax.tick_params(axis="y",labelsize=8,colors=TEXT_MID)
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.tight_layout(); return _fig_bytes(fig)


# ── 5. PYRAMIDE DES ÂGES ──────────────────────────────────────────────────────

def plot_age_pyramid(df, company=""):
    if "Tranche_age" not in df.columns or "Genre" not in df.columns: return None
    data=df[["Tranche_age","Genre"]].dropna()
    if data.empty: return None
    age_order=["20-30 ans","31-40 ans","41-50 ans","51 ans et plus"]
    age_order=[a for a in age_order if a in data["Tranche_age"].unique()] or sorted(data["Tranche_age"].unique())
    ct=pd.crosstab(data["Tranche_age"],data["Genre"]).reindex(age_order,fill_value=0)
    ct_pct=ct.div(ct.sum(axis=0).replace(0,np.nan),axis=1).fillna(0)*100
    h_vals=ct_pct.get("Homme",pd.Series(0.0,index=age_order))
    f_vals=ct_pct.get("Femme",pd.Series(0.0,index=age_order))
    h_n=ct.get("Homme",pd.Series(0,index=age_order))
    f_n=ct.get("Femme",pd.Series(0,index=age_order))
    max_val=max(h_vals.max(),f_vals.max(),1)*1.2; seuil=max_val*0.15
    fig,ax=plt.subplots(figsize=(9,max(4,len(age_order)*1.2+1.5)))
    bh=ax.barh(age_order,-h_vals,color=HOMME_C,edgecolor="white",height=0.6,label="Homme",zorder=3)
    bf=ax.barh(age_order,f_vals, color=FEMME_C,edgecolor="white",height=0.6,label="Femme", zorder=3)
    for bars,vals,ns,side in [(bh,h_vals,h_n,"left"),(bf,f_vals,f_n,"right")]:
        for bar,pct,n in zip(bars,vals,ns):
            if pct<=0: continue
            bw=abs(bar.get_width()); yc=bar.get_y()+bar.get_height()/2; lbl=f"{pct:.1f}%\n(n={n})"
            if bw>=seuil:
                ax.text(bar.get_x()+bar.get_width()/2,yc,lbl,ha="center",va="center",
                        fontsize=8,fontweight="bold",color="white",zorder=4)
            else:
                xp=bar.get_x()-0.4 if side=="left" else bar.get_x()+bar.get_width()+0.4
                ax.text(xp,yc,lbl,ha="right" if side=="left" else "left",
                        va="center",fontsize=8,fontweight="bold",color=DARK,zorder=4)
    ax.axvline(0,color=DARK,linewidth=0.9); ax.set_xlim(-max_val,max_val)
    ax.set_xticklabels([f"{abs(t):.0f}%" for t in ax.get_xticks()],fontsize=9)
    ax.set_facecolor(BG); fig.patch.set_facecolor("white")
    ax.grid(True,color=GRID_C,linewidth=0.8,axis="x",zorder=0); ax.set_axisbelow(True)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color("#D6E8F7")
    suffix=f" — {company}" if company else ""
    ax.set_title(f"Pyramide des âges{suffix}",fontsize=13,fontweight="bold",color=DARK,pad=14)
    ax.set_xlabel("% au sein de chaque genre",fontsize=10,color=TEXT_MID)
    ax.set_ylabel("Tranche d'âge",fontsize=10,color=TEXT_MID)
    ax.legend(loc="upper right",fontsize=9,framealpha=0.9)
    fig.tight_layout(); return _fig_bytes(fig)


# ── ORCHESTRATEUR ──────────────────────────────────────────────────────────────

class MBIVisualizations:
    def __init__(self, company=""):
        self.company = company

    def generate_all(self, df, metrics) -> Dict[str, bytes]:
        generators = {
            "mbi_radar":        lambda: plot_mbi_radar(df, metrics, self.company),
            "mbi_bars":         lambda: plot_mbi_bars(df, metrics, self.company),
            "burnout_donut":    lambda: plot_burnout_risk(df, metrics, self.company),
            "mbi_heatmap":      lambda: plot_mbi_heatmap(df, self.company),
            "age_pyramid":      lambda: plot_age_pyramid(df, self.company),
        }
        results = {}
        for name, fn in generators.items():
            try:
                r = fn()
                if r: results[name] = r
            except Exception as e:
                import warnings as _w; _w.warn(f"MBI viz '{name}' failed: {e}")
        return results

    def generate_for_report(self, df, metrics) -> Dict[str, bytes]:
        return self.generate_all(df, metrics)
