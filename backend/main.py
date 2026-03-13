# %%
from lib.questionnaires.karasek.questionnaire import KarasekQuestionnaire
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # 1. Initialisation
    kq = KarasekQuestionnaire()
    
    # 2. Exécution
    # Assure-toi d'avoir un fichier CSV de test dans data/
    results = kq.run_pipeline(
        input_file="backend/lib/data/sample_karasek.csv", 
        output_dir="reports/karasek"
    )
    
    # 3. Affichage rapide
    print(f"Analyse terminée. Lignes traitées : {results['rows']}")
    print(f"Rapport généré : {results['report_path']}")
    print(f"% Job Strain : {results['metrics']['strain_prevalence']['Job_strain']['pct']:.1f}%")

if __name__ == "__main__":
    main()
# %%