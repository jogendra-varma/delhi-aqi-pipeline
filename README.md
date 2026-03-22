# 🌫️ Delhi Air Quality Pipeline

An end-to-end Azure data engineering project tracking, 
analysing and forecasting Delhi's air quality.

## 🎯 Problem Statement
Delhi is consistently ranked among the world's most 
polluted capitals. This project builds a production-style 
data pipeline to ingest 10 years of historical AQI data, 
transform it through a medallion architecture, forecast 
next week's air quality using machine learning, and serve 
insights through an interactive dashboard.

## 🏗️ Architecture
- **Sources** — Kaggle (2015–2024), CPCB Portal, OpenAQ API (live)
- **Bronze Layer** — Raw data stored in Azure Blob Storage
- **Silver Layer** — Cleaned and standardised in Azure Databricks
- **Gold Layer** — Aggregated and forecast-ready for Power BI
- **Orchestration** — Azure Data Factory (scheduled pipelines)
- **Alerting** — Azure Logic Apps (email when AQI > 300)

## 🛠️ Tech Stack
Azure Data Factory | Azure Blob Storage | Azure Databricks  
Azure Synapse Analytics | Power BI | Python | PySpark  
Prophet | SQL | Git

## 📊 Key Features
- 10 years of Delhi AQI data across 4 monitoring stations
- Medallion architecture (Bronze → Silver → Gold)
- Event flag analysis (Diwali, crop burning, odd-even rule)
- 7-day AQI forecast using Facebook Prophet
- Live data ingestion via OpenAQ API
- Automated email alert when AQI crosses dangerous levels

## 📈 Monitoring Stations Covered
- Anand Vihar (most polluted zone)
- Lodhi Road (cleanest zone — contrast reference)
- Punjabi Bagh (west Delhi — industrial)
- ITO (central Delhi — traffic)

## 🗂️ Data Sources
- [Kaggle — Air Quality Data in India](https://www.kaggle.com/datasets/ankushpanday1/air-quality-data-in-india-2015-2024)
- [CPCB CCR Portal](https://app.cpcbccr.com/ccr)
- [OpenAQ API](https://openaq.org)

## 📁 Project Structure
delhi-aqi-pipeline/
├── notebooks/
│   ├── 01_bronze_ingestion.ipynb
│   ├── 02_silver_transformation.ipynb
│   ├── 03_gold_aggregation.ipynb
│   └── 04_forecasting.ipynb
├── scripts/
│   ├── extract_openaq.py
│   ├── transform_silver.py
│   └── calculate_aqi.py
├── sql/
│   └── gold_layer_schema.sql
├── dashboard/
│   └── screenshots/
└── README.md

## 🚧 Status
✅ Part 1 — Foundation complete
🔄 Part 2 — Silver layer complete

### Progress Log
- 2026-03-22 — Explored raw Kaggle dataset (3,653 Delhi rows, 2015–2024)
- 2026-03-22 — Built Bronze → Silver transformation in Databricks
- 2026-03-22 — Recalculated AQI from PM2.5 (original AQI unreliable)
- 2026-03-22 — Added event flags (Diwali, crop burning, COVID, odd-even)
- 2026-03-22 — Silver Delta table saved (3,653 rows, 24 columns)

## 👤 Author
Jogendra Varma Mogasati  
[LinkedIn](https://www.linkedin.com/in/jogendra-varma-26677223a?utm_source=share_via&utm_content=profile&utm_medium=member_android) | [Email](mjogendravarma@gmail.com)
