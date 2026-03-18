"""
pages/_export_utils.py
Utilitaires d'export partagés entre toutes les pages du dashboard.
Génère un fichier ZIP contenant le rapport Word + toutes les figures PNG.
"""

import io
import zipfile
from datetime import datetime
from typing import Dict, Optional


def build_zip(
    docx_bytes: Optional[bytes],
    figures: Dict[str, bytes],
    prefix: str = "wave_ci",
    company: str = "",
) -> bytes:
    """
    Construit un ZIP contenant :
      - Le rapport Word (.docx)
      - Toutes les figures PNG dans un sous-dossier figures/

    Parameters
    ----------
    docx_bytes : bytes du fichier .docx (None = non inclus)
    figures    : dict {nom_figure: png_bytes}
    prefix     : préfixe des noms de fichiers (ex: 'karasek', 'qvt', 'mbi')
    company    : nom de l'organisation (utilisé dans les noms de fichiers)

    Returns
    -------
    bytes du fichier ZIP
    """
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    company_slug = (
        company.lower()
        .replace(" ", "_")
        .replace("'", "")
        .replace("/", "_")[:30]
        if company
        else "rapport"
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:

        # ── Rapport Word ──────────────────────────────────────────────────────
        if docx_bytes:
            docx_name = f"{prefix}_{company_slug}_{date_str}.docx"
            zf.writestr(docx_name, docx_bytes)

        # ── Figures PNG ───────────────────────────────────────────────────────
        FIGURE_LABELS = {
            # Karasek
            "karasek_scatter":     "grille_mapp",
            "karasek_heatmap":     "heatmap_direction",
            "strain_bars":         "prevalence_rps",
            "rh_radar":            "radar_rh",
            "age_pyramid":         "pyramide_ages",
            "genre_barplot":       "repartition_genre",
            "tranche_age_barplot": "repartition_age",
            "direction_barplot":   "repartition_direction",
            "csp_barplot":         "repartition_csp",
            # QVT
            "qvt_radar":           "qvt_radar_dimensions",
            "qvt_bar_dims":        "qvt_barres_dimensions",
            # MBI
            "mbi_bar_dims":        "mbi_barres_dimensions",
            "burnout_radar":       "mbi_radar_burnout",
        }

        for key, png_bytes in figures.items():
            if not png_bytes:
                continue
            label = FIGURE_LABELS.get(key, key)
            fname = f"figures/{prefix}_{label}_{date_str}.png"
            zf.writestr(fname, png_bytes)

        # ── README dans le ZIP ────────────────────────────────────────────────
        readme = (
            f"Wave-CI — Export {prefix.upper()}\n"
            f"{'=' * 40}\n"
            f"Organisation : {company or 'N/A'}\n"
            f"Date         : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"Contenu de cette archive :\n"
            f"  • Rapport Word (.docx) — analyse complète\n"
            f"  • figures/ — {len(figures)} visualisation(s) PNG haute résolution\n\n"
            f"Seuils : théoriques uniquement — non cliniques.\n"
            f"Plateforme : Wave-CI\n"
        )
        zf.writestr("README.txt", readme)

    buf.seek(0)
    return buf.read()


def render_zip_button(
    docx_bytes: Optional[bytes],
    figures: Dict[str, bytes],
    prefix: str = "karasek",
    company: str = "",
    label: str = "📦 Télécharger tout (ZIP)",
):
    """
    Affiche un bouton Streamlit pour télécharger le ZIP complet.
    Doit être appelé depuis un contexte Streamlit actif.
    """
    import streamlit as st

    if not docx_bytes and not figures:
        st.info("Génère d'abord le rapport pour activer l'export ZIP.")
        return

    zip_bytes = build_zip(docx_bytes, figures, prefix=prefix, company=company)
    date_str  = datetime.now().strftime("%Y%m%d")
    filename  = f"wave_ci_{prefix}_{date_str}.zip"

    st.download_button(
        label=label,
        data=zip_bytes,
        file_name=filename,
        mime="application/zip",
        use_container_width=True,
    )
