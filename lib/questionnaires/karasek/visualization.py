# lib/questionnaires/karasek/visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd

class KarasekVisualizer:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir) / "figures"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_style("whitegrid")

    def plot_quadrants(self, df: pd.DataFrame) -> str:
        if "Karasek_quadrant" not in df.columns: return ""
        
        counts = df["Karasek_quadrant"].value_counts()
        plt.figure(figsize=(8, 6))
        counts.plot(kind='bar', color=['#22C55E', '#38A3E8', '#EF4444', '#94A3B8'])
        plt.title("Répartition par Quadrant (Seuil Théorique)")
        plt.ylabel("Nombre d'employés")
        plt.xticks(rotation=0)
        
        path = self.output_dir / "quadrants.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close()
        return str(path)

    def plot_scatter(self, df: pd.DataFrame) -> str:
        if "Dem_score" not in df.columns or "Lat_score" not in df.columns: return ""
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(df["Dem_score"], df["Lat_score"], 
                              c=df["Karasek_quadrant"].map({
                                  "Actif": "#22C55E", "Détendu": "#38A3E8", 
                                  "Tendu": "#EF4444", "Passif": "#94A3B8"
                              }), alpha=0.6)
        
        # Lignes de seuil
        plt.axvline(22.5, color='black', linestyle='--')
        plt.axhline(60.0, color='black', linestyle='--')
        
        plt.xlabel("Demande Psychologique")
        plt.ylabel("Latitude Décisionnelle")
        plt.title("Grille de Karasek - Scatterplot")
        
        path = self.output_dir / "scatter.png"
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close()
        return str(path)