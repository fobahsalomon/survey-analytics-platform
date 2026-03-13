from pathlib import Path
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict
import pandas as pd

class KarasekReporting:
    def __init__(self, config):
        self.config = config

    def _add_section_title(self, doc, text: str, level: int = 1):
        """Ajoute un titre de section avec mise en forme"""
        heading = doc.add_heading(text, level=level)
        heading.runs[0].font.color.rgb = RGBColor(15, 35, 64)  # #0F2340
        return heading

    def _add_kpi_paragraph(self, doc, label: str, pct: float, n: int):
        """Ajoute une ligne KPI formatée X% (N)"""
        p = doc.add_paragraph()
        runner = p.add_run(f"• {label}: ")
        runner.font.bold = True
        runner.font.color.rgb = RGBColor(47, 87, 127)  # #2F577F
        
        value_run = p.add_run(f"{pct:.1f}% ({n})")
        value_run.font.bold = True
        value_run.font.color.rgb = RGBColor(56, 163, 232)  # #38A3E8

    def generate_word_report(self, df: pd.DataFrame, metrics: Dict, output_dir: str) -> str:
        doc = Document()
        
        # Style global
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        
        # =========================================================================
        # EN-TÊTE
        # =========================================================================
        title = doc.add_heading(f"Rapport d'Analyse Karasek", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.runs[0].font.color.rgb = RGBColor(15, 35, 64)
        
        doc.add_paragraph(f"Organisation : {self.config.COMPANY_NAME}").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M')}").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph(f"Effectif analysé : {metrics['demographics']['total']}").alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()  # Espacement
        
        # =========================================================================
        # SECTION 1 : DONNÉES DÉMOGRAPHIQUES & MODES DE VIE
        # =========================================================================
        self._add_section_title(doc, "1. Données Démographiques & Modes de Vie", level=1)
        
        # 1.1 Données démographiques
        self._add_section_title(doc, "1.1 Données démographiques", level=2)
        demo = metrics['demographics']
        
        p = doc.add_paragraph()
        p.add_run(f"Hommes : ").bold = True
        p.add_run(f"{demo['men']['pct']:.1f}% ({demo['men']['n']})  |  ")
        p.add_run(f"Femmes : ").bold = True
        p.add_run(f"{demo['women']['pct']:.1f}% ({demo['women']['n']})  |  ")
        p.add_run(f"Âge moyen : ").bold = True
        p.add_run(f"{demo['avg_age']} ans")
        
        doc.add_paragraph()  # Espacement
        
        # 1.2 Indicateurs de modes de vie
        self._add_section_title(doc, "1.2 Indicateurs de modes de vie", level=2)
        lifestyle = metrics.get('lifestyle', {})
        
        lifestyle_labels = {
            "sedentarity": "Sédentarité (pas de sport)",
            "alcohol": "Consommation d'alcool",
            "tobacco": "Tabagisme",
            "chronic": "Maladie chronique",
            "overweight": "Surpoids & Obésité"
        }
        
        for key, label in lifestyle_labels.items():
            if key in lifestyle:
                self._add_kpi_paragraph(doc, label, lifestyle[key]['pct'], lifestyle[key]['n'])
        
        doc.add_paragraph()  # Espacement
        
        # =========================================================================
        # SECTION 2 : RÉSULTATS PRINCIPAUX
        # =========================================================================
        self._add_section_title(doc, "2. Résultats Principaux", level=1)
        
        # 2.1 Méthodologie
        self._add_section_title(doc, "2.1 Méthodologie (Seuils Théoriques)", level=2)
        doc.add_paragraph("Ce rapport utilise les seuils théoriques basés sur le point médian de l'échelle Likert (1-4).")
        
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text = "Dimension"
        hdr[1].text = "Seuil théorique"
        
        # En-têtes du tableau
        for cell in hdr:
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Lignes du tableau (Karasek + RH)
        all_scores = {
            **{k: v for k, v in self.config.THRESHOLDS.items() if k in ["Dem_score", "Lat_score", "SS_score"]},
            **{k: v for k, v in self.config.THRESHOLDS.items() if k in ["comp_score", "auto_score", "sup_score", "col_score"]},
            **{k: v for k, v in self.config.THRESHOLDS.items() if k in ["rec_score", "equ_score", "cult_score", "sat_score", "adq_resources_score", "adq_role_score"]}
        }
        
        for k, v in all_scores.items():
            row = table.add_row().cells
            row[0].text = self.config.SCORE_LABELS.get(k, k)
            row[1].text = str(v)
            row[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()  # Espacement
        
        # 2.2 Quadrants de Karasek
        self._add_section_title(doc, "2.2 Quadrants de Karasek", level=2)
        quadrants = metrics.get('quadrants', {})
        quadrant_order = ["Actif", "Détendu", "Tendu", "Passif"]
        
        for q in quadrant_order:
            if q in quadrants:
                self._add_kpi_paragraph(doc, q, quadrants[q]['pct'], quadrants[q]['count'])
        
        doc.add_paragraph()  # Espacement
        
        # 2.3 Prévalence des RPS
        self._add_section_title(doc, "2.3 Prévalence des RPS", level=2)
        strain = metrics.get('strain_prevalence', {})
        
        if "Job_strain" in strain:
            self._add_kpi_paragraph(doc, "Job Strain (Tension au travail)", strain['Job_strain']['pct'], strain['Job_strain']['n'])
        if "Iso_strain" in strain:
            self._add_kpi_paragraph(doc, "Iso-Strain (Isolement au travail)", strain['Iso_strain']['pct'], strain['Iso_strain']['n'])
        
        doc.add_paragraph()  # Espacement
        
        # 2.4 Indicateurs clés de stress au travail
        self._add_section_title(doc, "2.4 Indicateurs clés de stress au travail", level=2)
        stress = metrics.get('stress_indicators', {})
        
        stress_labels = {
            "autonomy": "Autonomie décisionnelle (élevée)",
            "workload": "Charge mentale (élevée)",
            "social_support": "Soutien social (élevé)"
        }
        
        for key, label in stress_labels.items():
            if key in stress:
                self._add_kpi_paragraph(doc, label, stress[key]['pct'], stress[key]['n'])
        
        doc.add_paragraph()  # Espacement
        
        # 2.5 Scores RH
        self._add_section_title(doc, "2.5 Climat Organisationnel (Scores RH)", level=2)
        rh = metrics.get('rh_scores', {})
        
        for col, data in rh.items():
            self._add_kpi_paragraph(doc, f"{data['label']} (niveau élevé)", data['pct'], data['n'])
        
        # =========================================================================
        # PIED DE PAGE
        # =========================================================================
        doc.add_paragraph()
        doc.add_paragraph()
        separator = doc.add_paragraph("─" * 80)
        separator.alignment = WD_ALIGN_PARAGRAPH.CENTER
        separator.runs[0].font.color.rgb = RGBColor(107, 136, 168)
        
        note = doc.add_paragraph("Note : Les seuils théoriques sont basés sur le point médian de l'échelle. ")
        note.add_run("Ces indicateurs sont conventionnels et non cliniques.")
        note.runs[1].font.italic = True
        note.runs[1].font.color.rgb = RGBColor(107, 136, 168)
        
        # =========================================================================
        # SAUVEGARDE
        # =========================================================================
        output_path = Path(output_dir) / "rapport_karasek.docx"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(output_path)
        
        return str(output_path)