# Questionnaire Analytics Platform

A modular data analysis platform designed to automate the processing, scoring, visualization, and reporting of workplace questionnaires.

The system provides a complete pipeline from raw survey datasets to analytical dashboards and automatically generated reports.

---

# Overview

This project was developed to automate the analysis of organizational surveys such as:

* Karasek (Job Demand-Control model)
* QVT (Quality of Work Life)
* MBI (Maslach Burnout Inventory)

The platform processes questionnaire datasets, computes relevant metrics, generates visualizations, and produces structured analytical reports.

The architecture is designed to be **modular and extensible**, allowing new questionnaires to be integrated with minimal changes.

---

# Key Features

* Automated dataset cleaning and preprocessing
* Questionnaire-specific scoring logic
* Statistical analysis and indicator computation
* Interactive dashboards
* Automatic Word report generation
* Modular architecture supporting multiple questionnaires

---

# Architecture

The platform is structured into three main components:

```
Frontend (React)
        │
        ▼
Backend API (Python)
        │
        ▼
Analytics Library
```

### Frontend

A React application used to:

* upload datasets
* select questionnaire types
* visualize analysis results
* download generated reports

### Backend

A Python API responsible for:

* receiving uploaded datasets
* triggering the analysis pipeline
* returning computed results to the frontend

### Analytics Library

A modular Python library implementing:

* data cleaning
* questionnaire scoring
* analytics computation
* chart generation
* report creation

Detailed architecture documentation is available in:

```
docs/architecture.md
```

---

# Project Structure

```
questionnaire-analytics-platform/

backend/        → API and pipeline orchestration
lib/            → Core analytics engine
frontend/       → React user interface
notebooks/      → Exploratory data analysis
docs/           → Project documentation
```

---

# Supported Questionnaires

Each questionnaire is implemented as a separate module.

Example structure:

```
lib/questionnaires/
    karasek/
    mbi/
    qvt/
```

Each module contains:

* configuration
* scoring logic
* analytical computations
* reporting logic

This design allows additional questionnaires to be added easily.

---

# Analysis Pipeline

The system follows a standardized data processing pipeline:

```
Dataset Upload
      │
      ▼
Data Cleaning
      │
      ▼
Questionnaire Scoring
      │
      ▼
Analytics Computation
      │
      ▼
Visualization Generation
      │
      ▼
Report Generation
```

---

# Example Workflow

1. Upload a questionnaire dataset (CSV)
2. Select the questionnaire type
3. Run the analysis
4. Visualize indicators and charts
5. Download the generated report

---

# Local Setup

## Backend

```
cd backend
pip install -r requirements.txt
python app/main.py
```

## Frontend

```
cd frontend
npm install
npm start
```

---

# Docker Deployment

The project can also be launched using Docker:

```
docker-compose up
```

This starts both the backend and frontend services.

---

# Sample Data

Example datasets are provided in:

```
lib/data/
```

These datasets are synthetic and are included for demonstration purposes only.

No confidential client data is included in this repository.

---

# Notebooks

The `notebooks/` directory contains exploratory notebooks used during development for:

* data exploration
* scoring validation
* statistical checks

---

# Design Principles

The platform was built with the following principles:

**Modularity**
Each questionnaire is implemented as an independent module.

**Extensibility**
New questionnaires can be added without modifying the core pipeline.

**Separation of Concerns**
Frontend, backend, and analytics logic are clearly separated.

**Reusability**
Shared utilities are centralized in the `lib/common` module.

---

# Future Improvements

Potential extensions include:

* support for additional questionnaires
* improved statistical analysis
* interactive dashboards
* database integration
* authentication for multi-user environments

---

# License

This project is provided for demonstration and educational purposes.

All datasets included in this repository are synthetic and do not contain any confidential information.

---

# Author

Salomon Fobah

Bachelor Student – Data Science & Programming
