# 💳 Financial Risk Dashboard

An end-to-end data science project analyzing a **$34B Lending Club loan portfolio** to predict credit default risk using SQL, Python, and Streamlit.

## 🎯 Business Problem
Credit risk teams need to identify high-risk loan segments before they default. This project builds a full analytics pipeline — from raw data ingestion to an interactive dashboard — to surface actionable risk insights across 2.26M loans.

## 📊 Key Results
- Analyzed **2,260,668 loans** totaling **$34B** in volume (2007–2018)
- Built an **XGBoost default prediction model** achieving **AUC-ROC of 0.73**
- Identified default rates ranging from **3.3% (Grade A) to 38.1% (Grade G)**
- Surfaced top default predictors: interest rate, DTI, and FICO score

## 🛠️ Tech Stack
| Layer | Tools |
|-------|-------|
| Database | PostgreSQL 15 |
| Data Pipeline | Python, psycopg2, pandas |
| Analysis | SQL (CTEs, window functions), pandas, seaborn |
| Modeling | XGBoost, scikit-learn |
| Dashboard | Streamlit |
| Version Control | Git, GitHub |

## 📁 Project Structure
## 🚀 How to Run

### 1. Set up the database
```bash
createdb lending_risk
psql -d lending_risk -f sql/schema.sql
python sql/load_data.py
```

### 2. Run the dashboard
```bash
streamlit run app.py
```

## 📈 Dashboard Features
- **KPI cards**: total loans, portfolio volume, avg interest rate, default rate
- **Grade analysis**: default rate and interest rate by loan grade A–G
- **Purpose analysis**: default rate across 14 loan purposes
- **FICO analysis**: default rate by credit score band
- **Time series**: monthly origination volume and default rate trend (2007–2018)
- **Interactive filters**: filter all charts by grade and loan term

## 📂 Dataset
[Lending Club Loan Data](https://www.kaggle.com/datasets/wordsforthewise/lending-club) — 2.26M accepted loans from 2007 to 2018 (Kaggle, free).

---
*Built by Sumaksharika Nainavarapu | [LinkedIn](https://linkedin.com/in/sumaksharika) | [Portfolio](https://sumaksharika.com)*

## 🌐 Live Demo
**[View Live Dashboard](https://financial-risk-dashboard-ovjmqv7edtxfdeczx8zctv.streamlit.app)**
