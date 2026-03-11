#%%
# =============================================================================
# POINT D'ENTRÉE PRINCIPAL - DÉMONSTRATION
# =============================================================================
"""
Exemple d'utilisation de la librairie avec le questionnaire Karasek.
"""

import pandas as pd
import os
from questionnaires.karasek import KarasekQuestionnaire


def main():
    """Exécute une analyse complète Karasek."""
    
    # 1. Chargement des données
    print("📊 Chargement des données...")
    df = pd.read_csv("data/data_Karasek.csv")
    print(f"   {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    # 2. Initialisation du questionnaire
    print("\n🔧 Initialisation du questionnaire Karasek...")
    karasek = KarasekQuestionnaire(df, "YODAN")
    
    # 3. Exécution de l'analyse complète
    output_path = "results/karasek"
    karasek.run_full_analysis(output_path)
    
    # 4. Résumé
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DE L'ANALYSE")
    print("="*60)
    summary = karasek.get_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Analyse terminée avec succès!")


if __name__ == "__main__":
    main()
    
    
# %%
