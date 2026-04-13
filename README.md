# SurveyLens

SurveyLens is a **survey intelligence system** that transforms raw HR and psychosocial questionnaires into structured, actionable insights for decision-making.

It combines **data processing, psychological scoring models, and interactive analytics dashboards** into a single end-to-end pipeline.

🔗 Live demo: https://surveylens.streamlit.app/

---

## 📌 Problem

Survey data from HR and field research is often:

- fragmented and inconsistently formatted  
- manually processed in spreadsheets  
- difficult to interpret at scale  
- slow to convert into actionable insights  

This leads to delays and underutilization of critical organizational data.

---

## 💡 Solution

SurveyLens automates the full pipeline from raw data to insights:

- standardized data ingestion (CSV / Excel)
- automated cleaning and validation
- questionnaire-specific scoring engines
- KPI computation and aggregation
- interactive dashboards for exploration
- exportable reports (Word + figures + ZIP)

The system is designed to support **data-driven decision-making in HR, research, and field studies**.

---

## 🏗 Architecture

SurveyLens is structured as a modular analytics pipeline:

```

Raw Data
↓
Ingestion Layer (file upload & parsing)
↓
Processing Layer (cleaning & validation)
↓
Scoring Engine (Karasek, QVT, MBI)
↓
Analytics Layer (KPIs, aggregation, segmentation)
↓
Visualization Layer (Streamlit dashboards)
↓
Export Layer (Word reports + figures + ZIP)

````

### Codebase structure

- `app.py` → navigation hub (no business logic)
- `pages/` → Streamlit interfaces per questionnaire
- `lib/common/` → shared utilities and abstractions
- `lib/questionnaires/` → modular scoring engines per model

This separation ensures **reproducibility, scalability, and maintainability**.

---

## 🎯 Use Cases

SurveyLens is designed for:

- HR departments analyzing employee well-being
- NGOs conducting field surveys
- Academic researchers in psychology / sociology
- Public health and organizational studies

---

## ⚙️ Key Features

- Multi-format data ingestion (CSV, Excel)
- Automated preprocessing and feature engineering
- Psychological scoring models:
  - Karasek (job strain, decision latitude)
  - QVT (quality of work life)
  - MBI (burnout risk)
- Interactive dashboards (Streamlit + Plotly)
- Dynamic filtering and segmentation
- Automated report generation (Word + visual exports)
- ZIP export of complete analysis results

---

## 🧠 Supported Models

### Karasek Model
Measures job strain through:
- psychological demand
- decision latitude
- social support
→ outputs: job strain zones, iso-strain risk

### QVT (Quality of Work Life)
Assesses organizational well-being across multiple dimensions  
→ outputs: global QVT score + distributions

### MBI (Maslach Burnout Inventory)
Evaluates burnout risk:
- emotional exhaustion
- depersonalization
- professional efficacy

---

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-4DABCF?style=flat&logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=flat&logo=python&logoColor=white)
![Statsmodels](https://img.shields.io/badge/Statsmodels-003B57?style=flat)
![python-docx](https://img.shields.io/badge/python--docx-0078D4?style=flat&logo=microsoft-word&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)

---

## 📊 Technical Highlights

- Modular pipeline architecture
- Separation of business logic and UI
- Reusable scoring engine per questionnaire
- Config-driven design (thresholds, mappings, labels)
- Reproducible analytics workflow
- Exportable reporting system

---

## 🚀 Getting Started

```bash
pip install -r requirements.txt
streamlit run app.py
````

---

## 📁 Sample Data

Example datasets are provided in `lib/data/` to:

* test the pipeline
* validate outputs
* demonstrate expected input format

---

## 🎯 Objective

* Data Science Internship (applied or research-oriented)
* AIMS Program (Applied Mathematics / Data Science)

---

📍 Abidjan, Côte d’Ivoire
🎓 Data Science student @ African School of Economics
