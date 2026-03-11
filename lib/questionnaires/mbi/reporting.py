# Fichier reporting.py pour le questionnaire
import os
import pandas as pd

def export_excel(questionnaire, output_path):
    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, "results.xlsx")
    with pd.ExcelWriter(file_path) as writer:
        if questionnaire.descriptives is not None:
            questionnaire.descriptives.to_excel(writer, sheet_name="descriptives")
        if questionnaire.crosstabs is not None:
            questionnaire.crosstabs.to_excel(writer, sheet_name="crosstabs")

def export_figures(questionnaire, output_path):
    figures_path = os.path.join(output_path, "figures")
    os.makedirs(figures_path, exist_ok=True)

def export_word(questionnaire, output_path):
    # TODO: Ajouter génération docx
    pass
