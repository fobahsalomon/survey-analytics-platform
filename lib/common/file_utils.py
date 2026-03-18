"""
lib/common/file_utils.py
Utilitaires de chargement de fichiers.
"""

import csv
import io
from pathlib import Path
import pandas as pd


EXCEL_SIGNATURES = (
    b"PK\x03\x04",
    b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1",
)


def _read_csv_buffer(buf: io.BytesIO, encoding_fallback: str) -> pd.DataFrame:
    buf.seek(0)
    try:
        return pd.read_csv(buf, sep=None, engine="python", encoding="utf-8-sig")
    except Exception:
        buf.seek(0)
        return pd.read_csv(buf, sep=None, engine="python", encoding=encoding_fallback)


def _looks_like_excel(raw: bytes) -> bool:
    return raw.startswith(EXCEL_SIGNATURES)


def _looks_like_csv(raw: bytes, encoding_fallback: str) -> bool:
    sample = raw[:4096]
    if not sample or b"\x00" in sample:
        return False

    for encoding in ("utf-8-sig", encoding_fallback):
        try:
            text = sample.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        return False

    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return False

    try:
        dialect = csv.Sniffer().sniff("\n".join(lines[:5]), delimiters=",;|\t")
    except csv.Error:
        return False

    return dialect.delimiter in "\t,;|"


def load_dataframe(source, file_name: str | None = None, encoding_fallback: str = "latin-1") -> pd.DataFrame:
    """
    Charge un DataFrame depuis:
    - un chemin (str ou Path)
    - des bytes
    - un objet file-like (BytesIO, UploadedFile Streamlit, etc.)

    Supporte CSV (auto-détection séparateur) et Excel.
    """
    # Résolution de la source
    if isinstance(source, (str, Path)):
        path = Path(source)
        name = file_name or path.name
        raw = path.read_bytes()
    elif isinstance(source, bytes):
        raw = source
        name = file_name or "data"
    else:
        # file-like (Streamlit UploadedFile, BytesIO...)
        raw = source.read() if hasattr(source, "read") else bytes(source)
        name = file_name or getattr(source, "name", "data")

    buf = io.BytesIO(raw)

    ext = Path(name).suffix.lower()

    if ext == ".csv":
        df = _read_csv_buffer(buf, encoding_fallback)
    elif ext in {".xlsx", ".xls", ".xlsm", ".xlsb", ".ods"}:
        df = pd.read_excel(buf)
    else:
        if _looks_like_excel(raw):
            df = pd.read_excel(buf)
        elif _looks_like_csv(raw, encoding_fallback):
            df = _read_csv_buffer(buf, encoding_fallback)
        else:
            raise ValueError("Format de fichier non reconnu. Utilisez un fichier CSV ou Excel valide.")

    df.columns = [str(c).strip() for c in df.columns]
    return df


def load_bytes_and_name(uploaded_file) -> tuple[bytes, str]:
    """Extrait (bytes, name) depuis un objet UploadedFile Streamlit."""
    raw = uploaded_file.read()
    return raw, getattr(uploaded_file, "name", "data")
