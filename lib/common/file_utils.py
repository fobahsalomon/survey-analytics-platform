# lib/common/file_utils.py
import pandas as pd
from pathlib import Path

class FileUtils:
    @staticmethod
    def load_csv_robust(file_path: str) -> pd.DataFrame:
        """
        Tente de charger un CSV avec différents encodages.
        """
        encodings = ["utf-8-sig", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                return pd.read_csv(file_path, encoding=enc, sep=None, engine="python")
            except Exception:
                continue
        raise ValueError(f"Impossible de lire le fichier {file_path} avec les encodages standards.")

    @staticmethod
    def save_csv(df: pd.DataFrame, file_path: str):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")