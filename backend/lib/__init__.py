# lib/__init__.py
"""
Analytics Library - Core Engine for Questionnaire Analysis
"""

from lib.questionnaires.karasek.questionnaire import KarasekQuestionnaire

__version__ = "1.0.0"
__all__ = [
    "KarasekQuestionnaire",
]

def get_questionnaire(name: str):
    """
    Factory function to get a questionnaire instance by name.
    """
    questionnaires = {
        "karasek": KarasekQuestionnaire,
    }
    
    if name.lower() not in questionnaires:
        raise ValueError(f"Questionnaire '{name}' not found. Available: {list(questionnaires.keys())}")
    
    return questionnaires[name.lower()]()