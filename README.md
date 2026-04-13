
# [SurveyLens](https://surveylens.streamlit.app/)

SurveyLens is a Streamlit application for analyzing HR and psychosocial risk (RPS) questionnaires.

The project allows you to:
- load a CSV or Excel file;
- clean the data;
- calculate questionnaire-specific scores;
- generate aggregated indicators;
- display an interactive dashboard;
- generate a Word report and a ZIP export containing all figures.

The repository currently includes 3 analysis modules:
- `Karasek`: workplace stress, Job Strain, Iso-Strain, quadrants;
- `QVT`: Quality of Life at Work (Qualité de Vie au Travail);
- `MBI`: burnout assessment using the Maslach Burnout Inventory.

### 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-4DABCF?style=flat&logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?style=flat&logo=python&logoColor=white)
![python-docx](https://img.shields.io/badge/python--docx-0078D4?style=flat&logo=microsoft-word&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white)

## Project Purpose

The application serves as a presentation layer on top of a core analysis engine.

The workflow is consistent:
1. The user uploads a file;
2. The file is converted into a pandas DataFrame;
3. The questionnaire pipeline cleans, scores, and classifies responses;
4. Analytics compute KPIs and distributions;
5. Visualizations and reporting consume these results;
6. The dashboard renders everything in Streamlit.

## Project Structure

```text
survey-analytics-platform/
├── app.py
├── README.md
├── architecture.md
├── requirements.txt
├── pages/
│   ├── 1_karasek.py
│   ├── 2_qvt.py
│   ├── 3_mbi.py
│   ├── _ui_shared.py
│   └── _export_utils.py
└── lib/
    ├── common/
    │   ├── __init__.py
    │   ├── base_questionnaire.py
    │   ├── common_cleaning.py
    │   └── file_utils.py
    ├── data/
    │   ├── sample_karasek1.csv
    │   ├── sample_karasek2.csv
    │   ├── sample_qvt.csv
    │   └── sample_mbi.csv
    └── questionnaires/
        ├── karasek/
        ├── qvt/
        └── mbi/
```

## Directory Roles

### `app.py`

Landing page. It does not compute scores. It acts solely as a navigation hub to the three dashboard modules.

### `pages/`

Contains the Streamlit pages.

Each questionnaire page:
- handles file uploads;
- executes the analysis pipeline;
- applies filters;
- displays KPIs, charts, and tables;
- manages Word and ZIP exports.

The two utility files are:
- `pages/_ui_shared.py`: reusable UI components;
- `pages/_export_utils.py`: ZIP logic and download buttons.

### `lib/common/`

Contains the shared foundation:
- file reading;
- common data cleaning;
- socio-demographic enrichment;
- abstract questionnaire interface.

### `lib/questionnaires/`

Each subfolder follows the same structure:
- `config.py`: constants, thresholds, mappings, labels, colors;
- `questionnaire.py`: main analysis pipeline;
- `analytics.py`: aggregated metrics for the dashboard;
- `visualizations.py`: PNG figure generation;
- `reporting.py`: Word document generation.

## Technical Pipeline

The main data flow is:

```text
Raw File
  -> load_dataframe(...)
  -> Questionnaire.clean(...)
  -> Questionnaire.score(...)
  -> Questionnaire.classify(...)
  -> Questionnaire.analytics(...)
  -> Visualizations.generate_all(...)
  -> Reporting.generate(...)
```

## Installation

### Prerequisites

- Python 3.11 or newer recommended
- `pip`

### Setup

```bash
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

## Key Dependencies

- `streamlit`: web interface
- `pandas`: data manipulation
- `numpy`: numerical computing
- `plotly`: interactive charts
- `matplotlib` & `seaborn`: static figure exports
- `python-docx`: Word report generation

## Sample Files

Sample datasets are available in [lib/data](lib/data).

They are used to:
- quickly test the application;
- understand the expected input format;
- validate visualizations and reports.

## Data Handling

The project automatically removes sensitive or irrelevant columns:
- first name;
- last name;
- email;
- phone number;
- empty or near-empty columns.

It also enriches the data when possible:
- age brackets;
- tenure brackets;
- BMI;
- derived categories for cross-tabulations.

If a file lacks an `Age` column but contains age brackets, the project estimates the average age and supports age-based filtering from the bracket data.

## Supported Questionnaires

### Karasek

Purpose:
- measure psychological demand;
- assess decision latitude;
- evaluate social support;
- identify workplace tension zones.

Key Outputs:
- Karasek quadrants;
- Job Strain;
- Iso-Strain;
- complementary HR metrics.

### QVT (Quality of Life at Work)

Purpose:
- measure organizational well-being across multiple dimensions.

Key Outputs:
- global QVT score;
- distribution per dimension;
- satisfied / neutral / dissatisfied breakdown.

### MBI (Maslach Burnout Inventory)

Purpose:
- assess burnout risk.

Key Outputs:
- emotional exhaustion;
- cynicism / depersonalization;
- professional efficacy;
- composite burnout risk score.

## Reporting & Exports

Each page can generate:
- a Word report (`.docx`);
- a ZIP file containing the report and all PNG figures.

Reporting relies on pre-computed aggregated metrics. It does not recalculate business logic from scratch.

## Adding a New Questionnaire

The simplest approach is to copy an existing module's structure.

Steps:
1. create `lib/questionnaires/your_module/`;
2. add `config.py`;
3. add `questionnaire.py`;
4. add `analytics.py`;
5. add `visualizations.py` if needed;
6. add `reporting.py`;
7. create a corresponding Streamlit page in `pages/`.

The new questionnaire class must inherit from `BaseQuestionnaire`.

## Code Philosophy

The project intentionally separates:
- business logic;
- presentation layer;
- export mechanisms;
- configuration/constants.

This separation enables:
- updating thresholds without touching the dashboard;
- redesigning the UI without breaking calculations;
- reusing the same metrics for both charts and reports.

## Additional Documentation

The [architecture.md](architecture.md) file provides in-depth details on:
- project layers;
- role of key files;
- complete data lifecycle;
- questionnaire-specific logic;
- development conventions.
