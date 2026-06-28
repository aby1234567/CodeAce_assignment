# Middle Eastern Patient Dashboard

A Streamlit dashboard replicating a Power BI report built on synthetic Middle Eastern patient data (2021–2023). Covers patient demographics, hospital distribution, diagnosis patterns, and visit behaviour across 9,463 records.

---

## Project Structure

```
├── dashboard.py                                  # Streamlit app
├── patient_data_cleaned_with_age_category.xlsx   # Cleaned dataset (required at runtime)
├── patient_data_check.ipynb    
├── README.md                 # Data quality check & transformation notebook
└── requirements.txt
```

---

## Setup

**Requirements:** Python 3.9+

```bash
pip install -r requirements.txt
```

**Run:**

```bash
streamlit run dashboard.py
```

The app expects `patient_data_cleaned_with_age_category.xlsx` in the same directory.

---

## Data Preparation

The raw file (`fake_data_middle_eastern_patient_data_2021_2023_with_master_data.xlsx`) was validated and transformed using `patient_data_check.ipynb` before being used in the dashboard.

**Quality checks performed:**
- No missing values across all 13 columns
- No duplicate rows or UIDs
- All visit dates confirmed within 2021–2023
- Categorical fields (nationality, sex, hospital, diagnosis) validated against expected values
- Age range verified (15–91), no impossible values
- No whitespace issues in text columns

**Transformation applied:**
- `Age Category` column derived from `Age` using the following buckets:

| Age Range | Category |
|---|---|
| 0 – 17 | Children |
| 18 – 35 | Youth |
| 36 – 59 | Middle Age |
| 60+ | Senior Citizen |

---

## Dashboard Tabs

| Tab | Content |
|---|---|
| **Summary** | KPI cards, patient map by nationality, hospital bar chart, sex ratio donut, age category donut |
| **Periodic Movement** | Year-on-year, quarter-on-quarter, and month-on-month patient volume trends with % change overlays |
| **Diagnosis vs Patients** | Patient count across all 38 diagnoses |
| **Diagnosis vs Age** | Average patient age per diagnosis |
| **Patient Visits** | Visit volume by day of week and by 3-hour time window, split by sex |

All tabs include filters (nationality, year, hospital, diagnosis where applicable) that dynamically update the charts.

---

## Dataset Summary

| Field | Detail |
|---|---|
| Records | 9,463 |
| Years | 2021, 2022, 2023 |
| Nationalities | 16 |
| Hospitals | 10 |
| Diagnoses | 38 |
| Doctors | 1,000 unique |
| Age range | 15 – 91 |

> **Note:** This is a synthetic dataset generated for demonstration purposes. It does not represent real patient records.
