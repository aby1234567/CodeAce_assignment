# Middle Eastern Patient Dashboard

A Streamlit dashboard replicating a Power BI report built on synthetic Middle Eastern patient data (2021–2023). The dashboard covers patient demographics, hospital distribution, diagnosis patterns, and visit behaviour across **9,463 patient records**.

---

## Project Structure

```text
├── dashboard.py                                   # Streamlit application
├── patient_data_cleaned_with_age_category.xlsx    # Cleaned dataset (required at runtime)
├── patient_data_check.ipynb                       # Data quality checks and transformation notebook
├── README.md                                      # Project documentation
└── requirements.txt                               # Python dependencies
```

---

## Setup

### Requirements

- Python 3.9+

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run dashboard.py
```

The application expects the file:

```text
patient_data_cleaned_with_age_category.xlsx
```

to be present in the same directory as `dashboard.py`.

---

## Data Preparation

The original dataset:

```text
fake_data_middle_eastern_patient_data_2021_2023_with_master_data.xlsx
```

was validated and transformed using:

```text
patient_data_check.ipynb
```

before being used by the dashboard.

### Data Quality Checks

The following validations were performed:

- No missing values across all 13 columns
- No duplicate rows or duplicate patient UIDs
- All visit dates confirmed within the period 2021–2023
- Categorical fields validated against expected values:
  - Nationality
  - Sex
  - Hospital
  - Diagnosis
- Age range verified between **15 and 91 years**
- No impossible or invalid age values detected
- No leading or trailing whitespace issues in text columns

### Transformation Applied

An **Age Category** column was derived from the `Age` field using the following buckets:

| Age Range | Category |
|----------|----------|
| 0–17 | Children |
| 18–35 | Youth |
| 36–59 | Middle Age |
| 60+ | Senior Citizen |

---

## Dashboard Tabs

| Tab | Content |
|-----|---------|
| **Summary** | KPI cards, nationality map, hospital distribution, sex ratio and age category charts |
| **Periodic Movement** | Year-on-year, quarter-on-quarter and month-on-month patient trends |
| **Diagnosis vs Patients** | Patient counts across diagnoses |
| **Diagnosis vs Age** | Average patient age by diagnosis |
| **Patient Visits** | Visit behaviour by weekday and time window, segmented by sex |

### Available Filters

All dashboard tabs include dynamic filters where applicable:

- Nationality
- Year
- Hospital
- Diagnosis

Charts and KPIs update automatically based on selected filters.

---

## Dataset Summary

| Field | Detail |
|------|-------|
| Records | 9,463 |
| Years | 2021, 2022, 2023 |
| Nationalities | 16 |
| Hospitals | 10 |
| Diagnoses | 38 |
| Doctors | 1,000 unique |
| Age Range | 15–91 |

---

# KPI and Chart Calculations

All calculations update dynamically based on the active filters in their respective dashboard tabs.

---

## 1. Summary Tab (KPIs)

### Total Patients
Calculated as the total number of rows in the filtered dataset.

### Nationalities
Distinct count of unique values in the `Nationality` column.

### Average Patient Age
Arithmetic mean of the `Age` column, rounded down to the nearest integer.

### Male / Female Patients
Count of records where `Sex` equals:

- `Male`
- `Female`

### Total Hospitals
Distinct count of values in `Hospital Name`.

### Total Doctors
Distinct count of values in `Doctor ID`.

### Diagnoses
Distinct count of values in `Diagnosis Name`.

### Patient-to-Doctor Ratio
Calculated as:

```text
Total Patient Records / Unique Doctor IDs
```

---

## 2. Summary Tab (Charts)

### Patients by Nationality (Map)

Patient counts grouped by `Nationality`.

Marker sizes are scaled relative to the largest nationality count to improve readability.

### Patients by Hospital (Bar Chart)

Patient counts grouped by `Hospital Name` and displayed as a horizontal bar chart sorted in ascending order.

### Sex Ratio (Donut Chart)

Patient counts grouped by `Sex`, displayed as percentages of the total filtered population.

### Age Category Distribution (Donut Chart)

Patient counts grouped by `Age Category`, displayed as percentages of the total filtered population.

---

## 3. Periodic Movement Tab

### Yearly Movement

- Data grouped by `Year`
- Bar chart shows patient counts per year
- Line chart shows Year-over-Year percentage change

Calculation:

```text
YoY % = (Current Year Count - Previous Year Count) / Previous Year Count
```

The earliest year uses a baseline value of `0.00%`.

---

### Quarterly Movement

- Data grouped by `Year` and `Quarter`
- Displays patient counts per quarter
- Calculates Quarter-over-Quarter percentage change

Calculation:

```text
QoQ % = (Current Quarter Count - Previous Quarter Count) / Previous Quarter Count
```

---

### Monthly Movement

- Data grouped by `Year` and `Month`
- Displays patient counts per month
- Calculates Month-over-Month percentage change

Calculation:

```text
MoM % = (Current Month Count - Previous Month Count) / Previous Month Count
```

---

## 4. Diagnosis vs Patients Tab

### Patients by Diagnosis

Patient visits grouped by `Diagnosis Name`.

Calculation:

```text
Count of patient records for each diagnosis
```

---

## 5. Diagnosis vs Age Tab

### Average Age by Diagnosis

For each diagnosis:

```text
Average Age = Mean(Age)
```

Values are rounded to the nearest whole number.

Empty diagnosis groups created by filtering are excluded from the calculation.

---

## 6. Patient Visits Tab

### Patients Visit by Day

The day of the week is extracted from `Patient Visit Date`.

Patient visits are grouped and ordered as:

1. Sunday
2. Monday
3. Tuesday
4. Wednesday
5. Thursday
6. Friday
7. Saturday

---

### Patients Visit by Time Window and Sex

The hour component of `Patient Visit Date` is extracted and grouped into 3-hour windows:

- 00:00–03:00
- 03:00–06:00
- 06:00–09:00
- 09:00–12:00
- 12:00–15:00
- 15:00–18:00
- 18:00–21:00
- 21:00–24:00

Patient counts are then grouped by:

- Time Window
- Sex

This produces separate trend lines for male and female patient visits throughout the day.

---

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- OpenPyXL

---
