"""
lib/questionnaires/qvt/visualizations.py
Visualisations QVT — retourne des bytes PNG.
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
CAT_COLORS={"Satisfaisant":GREEN,"Mitigé":ORANGE,"Insatisfaisant":RED}
HOMME_C="#4472C4"; FEMME_C="#E91E8C"

def _fig_bytes(fig):
    """Sérialise une figure Matplotlib en PNG puis la ferme."""
    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=150,bbox_inches="tight",facecolor=fig.get_facecolor())
    plt.close(fig); buf.seek(0); return buf.read()

def _base(ax,title="",xlabel="",ylabel="",wrap=58):
    """Applique le style graphique partagé des visualisations QVT."""
    ax.set_facecolor(BG); ax.figure.patch.set_facecolor("white")
    ax.grid(True,color=GRID_C,linewidth=0.8,axis="x",zorder=0); ax.set_axisbelow(True)
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color("#D6E8F7")
    ax.tick_params(colors=TEXT_MID,labelsize=9)
    if title: ax.set_title("\n".join(textwrap.wrap(title,wrap)),fontsize=13,fontweight="bold",color=DARK,pad=14)
    if xlabel: ax.set_xlabel(xlabel,fontsize=10,color=TEXT_MID,labelpad=8)
    if ylabel: ax.set_ylabel("\n".join(textwrap.wrap(ylabel,22)),fontsize=10,color=TEXT_MID,labelpad=8)


def plot_qvt_radar(df, metrics, company=""):
    """Produit le radar des dimensions QVT basé sur le pourcentage satisfaisant."""
    dims=metrics.get("dimensions",{})
    if not dims: return None
    labels=[d["label"] for d in dims.values()]
    vals=[d.get("categories",{}).get("Satisfaisant",{}).get("pct",0) for d in dims.values()]
    if len(labels)<3: return None
    N=len(labels); angles=np.linspace(0,2*np.pi,N,endpoint=False).tolist()
    vc=vals+[vals[0]]; ac=angles+[angles[0]]
    fig,ax=plt.subplots(figsize=(7,7),subplot_kw={"polar":True})
    fig.patch.set_facecolor("white"); ax.set_facecolor(BG)
    ax.plot(ac,[60]*(N+1),color=ORANGE,linestyle="--",linewidth=1.2,alpha=0.5)
    ax.fill(angles,[60]*N,color=ORANGE,alpha=0.03)
    ax.plot(ac,vc,color=GREEN,linewidth=2.3,zorder=3)
    ax.fill(angles,vals,color=GREEN,alpha=0.15,zorder=2)
    ax.scatter(angles,vals,color=GREEN,s=55,zorder=4,edgecolors="white",linewidths=1.5)
    for a,v in zip(angles,vals):
        ax.annotate(f"{v:.0f}%",xy=(a,v),xytext=(a,v+7),ha="center",va="center",
                    fontsize=8,fontweight="bold",color=DARK)
    ax.set_xticks(angles)
    ax.set_xticklabels(["\n".join(textwrap.wrap(l,13)) for l in labels],fontsize=8,color=DARK)
    ax.set_ylim(0,100); ax.set_yticks([25,50,75,100])
    ax.set_yticklabels(["25%","50%","75%","100%"],fontsize=7,color=TEXT_MID)
    ax.yaxis.grid(True,color=GRID_C,linewidth=0.8); ax.xaxis.grid(True,color=GRID_C,linewidth=0.8)
    ax.spines["polar"].set_color("#D6E8F7")
    suffix=f" — {company}" if company else ""
    ax.set_title(f"Radar QVT{suffix}\n(% Satisfaisants par dimension)",
                 fontsize=11,fontweight="bold",color=DARK,pad=22)
    handles=[mpatches.Patch(color=GREEN,alpha=0.7,label="% Satisfaisant"),
             plt.Line2D([0],[0],color=ORANGE,linestyle="--",linewidth=1.2,label="Référence 60%")]
    ax.legend(handles=handles,loc="lower right",bbox_to_anchor=(1.3,-0.05),fontsize=8,framealpha=0.9)
    fig.tight_layout(); return _fig_bytes(fig)


def plot_qvt_bars(df, metrics, company=""):
    """Produit des barres groupées par dimension et catégorie QVT."""
    dims=metrics.get("dimensions",{}); 
    if not dims: return None
    dim_labels=[d["label"] for d in dims.values()]
    cats=["Satisfaisant","Mitigé","Insatisfaisant"]
    x=np.arange(len(dim_labels)); width=0.26
    fig,ax=plt.subplots(figsize=(12,5))
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
    ax.set_xticklabels(["\n".join(textwrap.wrap(l,14)) for l in dim_labels],fontsize=8,color=DARK)
    ax.set_ylim(0,115)
    suffix=f" — {company}" if company else ""
    _base(ax,title=f"Répartition QVT par dimension{suffix}",ylabel="Pourcentage (%)")
    ax.grid(True,color=GRID_C,linewidth=0.8,axis="y",zorder=0)
    ax.legend(title="Catégorie",fontsize=9,title_fontsize=9,framealpha=0.9)
    fig.tight_layout(); return _fig_bytes(fig)


def plot_qvt_heatmap(df, company=""):
    """Produit une heatmap des scores moyens QVT par direction."""
    dir_col=next((c for c in df.columns if c.strip().lower()=="direction"),None)
    dim_cols=[f"{d}_score" for d in DIMENSIONS if f"{d}_score" in df.columns]
    if not dir_col or not dim_cols: return None
    pivot=df.groupby(dir_col)[dim_cols].mean().round(2)
    if pivot.empty: return None
    rename={f"{d}_score":DIMENSIONS[d] for d in DIMENSIONS if f"{d}_score" in pivot.columns}
    pivot.rename(columns=rename,inplace=True)
    fig_h=max(3.5,0.5*len(pivot)+1.5)
    fig,ax=plt.subplots(figsize=(11,fig_h)); fig.patch.set_facecolor("white")
    cmap=sns.diverging_palette(10,140,s=70,l=55,as_cmap=True)
    sns.heatmap(pivot,ax=ax,cmap=cmap,vmin=1,vmax=5,annot=True,fmt=".1f",
                annot_kws={"size":9,"weight":"bold"},linewidths=0.5,
                linecolor="#F0F7FF",cbar_kws={"label":"Score moyen (1–5)"})
    suffix=f" — {company}" if company else ""
    ax.set_title(f"Scores QVT moyens par Direction{suffix}",
                 fontsize=12,fontweight="bold",color=DARK,pad=12)
    ax.set_xlabel("Dimension QVT",fontsize=10,color=TEXT_MID)
    ax.set_ylabel("Direction",fontsize=10,color=TEXT_MID)
    ax.tick_params(axis="x",labelsize=8,rotation=30,colors=TEXT_MID)
    ax.tick_params(axis="y",labelsize=8,colors=TEXT_MID)
    for spine in ax.spines.values(): spine.set_visible(False)
    fig.tight_layout(); return _fig_bytes(fig)


def plot_qvt_global_dist(df, metrics, company=""):
    """Produit l'histogramme de distribution du score QVT global."""
    if "qvt_global_score" not in df.columns: return None
    vals=pd.to_numeric(df["qvt_global_score"],errors="coerce").dropna()
    if vals.empty: return None
    fig,ax=plt.subplots(figsize=(8,4.5))
    ax.hist(vals,bins=20,color=ACCENT,alpha=0.7,edgecolor="white",zorder=3)
    med=vals.median()
    ax.axvline(med,color=ORANGE,linestyle="--",linewidth=1.8,zorder=4)
    ymax=ax.get_ylim()[1]
    ax.text(med+0.05,ymax*0.88,f"Médiane : {med:.1f}",color=ORANGE,
            fontsize=9,fontweight="bold")
    suffix=f" — {company}" if company else ""
    _base(ax,title=f"Distribution du score QVT global{suffix}",
          xlabel="Score QVT global",ylabel="Effectif")
    ax.grid(True,color=GRID_C,linewidth=0.8,axis="y",zorder=0)
    fig.tight_layout(); return _fig_bytes(fig)


def plot_age_pyramid(df, company=""):
    """Produit une pyramide des âges Homme/Femme à partir des tranches d'âge."""
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


class QVTVisualizations:
    """Orchestre la génération des visuels QVT exportables."""
    def __init__(self, company=""):
        """Mémorise le nom de l'organisation pour les titres de figures."""
        self.company = company

    def generate_all(self, df, metrics) -> Dict[str, bytes]:
        """Génère toutes les figures QVT disponibles sous forme de PNG bytes."""
        generators = {
            "qvt_radar":       lambda: plot_qvt_radar(df, metrics, self.company),
            "qvt_bars":        lambda: plot_qvt_bars(df, metrics, self.company),
            "qvt_heatmap":     lambda: plot_qvt_heatmap(df, self.company),
            "qvt_global_dist": lambda: plot_qvt_global_dist(df, metrics, self.company),
            "age_pyramid":     lambda: plot_age_pyramid(df, self.company),
        }
        results = {}
        for name, fn in generators.items():
            try:
                r = fn()
                if r: results[name] = r
            except Exception as e:
                import warnings as _w; _w.warn(f"QVT viz '{name}' failed: {e}")
        return results

    def generate_for_report(self, df, metrics) -> Dict[str, bytes]:
        """Retourne les figures QVT destinées au rapport Word."""
        return self.generate_all(df, metrics)
