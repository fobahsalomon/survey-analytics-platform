# Architecture

## Overview

**Questionnaire Analytics Platform** is a modular system designed to automate the analysis of workplace questionnaires and generate analytical reports and dashboards.

The platform is composed of three main layers:

1. **Frontend** – React application used for dataset upload, analysis visualization, and report download.
2. **Backend API** – Python service responsible for orchestrating the analysis pipeline.
3. **Analytics Library (`lib/`)** – Core engine that implements questionnaire logic, scoring, data cleaning, and report generation.

The system is designed to support multiple questionnaires, each with its own analysis logic while sharing a common processing pipeline.

---

# High Level Architecture

```
User
  │
  │ Upload dataset
  ▼
Frontend (React)
  │
  │ REST API request
  ▼
Backend API (Python)
  │
  │ calls
  ▼
Analytics Library
  │
  ├── Data Cleaning
  ├── Questionnaire Scoring
  ├── Chart Generation
  └── Word Report Generation
  │
  ▼
Results returned to frontend
```

---

# Project Structure

```
questionnaire-analytics-platform/
```

The repository is organized into several logical components.

## Backend

Responsible for API exposure and orchestration of the analysis pipeline.

```
backend/
```

### `app/main.py`

Application entry point. Initializes the API server and registers routes.

### `api/`

Handles HTTP endpoints.

```
routes.py
controllers.py
```

* **routes.py** defines API endpoints.
* **controllers.py** handles request validation and calls backend services.

Example endpoint:

```
POST /analyze
```

Input:

* questionnaire type
* dataset file

Output:

* analysis results
* generated charts
* downloadable report

### `services/`

Contains business logic that connects the API with the analytics library.

```
pipeline_service.py
report_service.py
```

Responsibilities:

* running analysis pipelines
* managing report generation
* coordinating questionnaire modules

### `core/`

Infrastructure-level utilities.

```
config.py
logger.py
```

* application configuration
* logging system

---

# Analytics Library

```
lib/
```

This module contains the **core analytical engine** used by the platform.

It is designed to support multiple questionnaires while sharing common utilities.

---

## Common Module

```
lib/common/
```

Shared components used across questionnaires.

### `base_questionnaire.py`

Defines the base interface for all questionnaires.

Each questionnaire must implement:

* data cleaning
* scoring logic
* analytics generation
* reporting

This ensures a consistent structure across modules.

### `common_cleaning.py`

Generic dataset preprocessing utilities such as:

* column normalization
* missing value handling
* encoding transformations

### `file_utils.py`

Utilities for file handling and dataset loading.

---

## Data Samples

```
lib/data/
```

Contains example datasets used for testing and demonstrations.

Files include:

* `sample_karasek.py`
* `sample_qvt.py`
* `sample_mbi.py`

These datasets allow testing the platform without exposing real client data.

---

## Questionnaire Modules

```
lib/questionnaires/
```

Each questionnaire has its own dedicated module.

Example:

```
karasek/
```

Structure:

```
config.py
questionnaire.py
analytics.py
reporting.py
```

Responsibilities:

### `config.py`

Defines questionnaire metadata such as:

* column mappings
* scoring rules
* dimensions

### `questionnaire.py`

Main class implementing the questionnaire logic.

Responsibilities:

* validation
* orchestration of cleaning and scoring
* returning structured results

### `analytics.py`

Computes indicators and derived metrics such as:

* score distributions
* quadrant analysis
* statistical summaries

### `reporting.py`

Generates the final Word report including:

* charts
* statistical tables
* textual interpretation

---

# Frontend

```
frontend/
```

The frontend is a React application responsible for interacting with users.

Key features:

* dataset upload
* questionnaire selection
* visualization of results
* report download

---

## Components

```
components/
```

### `UploadDataset.jsx`

Handles CSV upload and sends the dataset to the backend.

### `Dashboard.jsx`

Displays computed indicators and charts.

### `ChartViewer.jsx`

Reusable chart rendering component.

---

## Pages

```
pages/
```

### `Home.jsx`

Landing page of the application.

### `Analysis.jsx`

Main interface for launching and visualizing questionnaire analysis.

---

## Services

```
services/api.js
```

Centralized API communication layer between React and the backend.

Responsibilities:

* sending dataset to API
* retrieving analysis results
* handling errors

---

# Data Science Exploration

```
notebooks/
```

Contains Jupyter notebooks used for:

* exploratory data analysis
* testing scoring logic
* validating statistical outputs

These notebooks are not part of the production pipeline but help validate analytical methods.

---

# Documentation

```
docs/
```

Project documentation including:

* architecture overview
* screenshots of the platform
* implementation notes

---

# Deployment

Deployment is managed using Docker.

```
docker-compose.yml
```

The container stack typically includes:

* backend service
* frontend service

This allows the entire platform to be started locally using:

```
docker-compose up
```

---

# Design Principles

The system follows several architectural principles:

### Modular Questionnaire Design

Each questionnaire is implemented as an independent module, allowing the platform to easily support additional surveys.

### Separation of Concerns

The project separates responsibilities between:

* UI layer
* API orchestration
* analytics engine

### Reusability

Common utilities are centralized to avoid duplication and ensure consistency across questionnaire implementations.

### Extensibility

New questionnaires can be added by implementing a new module in:

```
lib/questionnaires/
```

following the base questionnaire interface.
