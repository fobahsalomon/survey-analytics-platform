# lib/questionnaires/karasek/reporting.py
from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from typing import Dict
import pandas as pd

class KarasekReporting:
    def __init__(self, config):
        self.config = config

    def generate_word_report(self, df: pd.DataFrame, metrics: Dict, output_dir: str) -> str:
        doc = Document()
        
        # Titre
        doc.add_heading(f"Rapport d'Analyse Karasek - {self.config.COMPANY_NAME}", 0)
        doc.add_paragraph(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        doc.add_paragraph(f"Effectif analysé : {metrics['demographics']['total']}")
        
        # Section 1 : Seuils
        doc.add_heading("1. Méthodologie (Seuils Théoriques)", level=1)
        doc.add_paragraph("Ce rapport utilise les seuils théoriques basés sur le point médian de l'échelle.")
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text = "Dimension"
        hdr[1].text = "Seuil"
        for k, v in self.config.THRESHOLDS.items():
            if k in ["Dem_score", "Lat_score", "SS_score"]:
                row = table.add_row().cells
                row[0].text = self.config.SCORE_LABELS.get(k, k)
                row[1].text = str(v)
        
        # Section 2 : Résultats
        doc.add_heading("2. Résultats Principaux", level=1)
        
        doc.add_heading("Quadrants de Karasek", level=2)
        for q, data in metrics.get("quadrants", {}).items():
            doc.add_paragraph(f"- {q} : {data['pct']:.1f}% (n={data['count']})")
            
        doc.add_heading("Prévalence des RPS", level=2)
        for k, v in metrics.get("strain_prevalence", {}).items():
            doc.add_paragraph(f"- {k} : {v['pct']:.1f}%")
            
        # Section 3 : Graphiques (si générés)
        # Note: Dans une implémentation complète, on passerait les chemins des images depuis le questionnaire
        # doc.add_picture('path_to_image.png', width=Inches(6))
        
        # Sauvegarde
        output_path = Path(output_dir) / "rapport_karasek.docx"
        doc.save(output_path)
        return str(output_path)