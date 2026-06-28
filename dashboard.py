import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Patient Dashboard", layout="wide", page_icon="🏥")

# Chart accent colours (used in Plotly traces only)
TEAL      = "#00B0A0"
PINK      = "#E83E8C"
LINE_CLR  = "#1a3a5c"   # dark navy — clearly visible on light/white bg


# ── Data ────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("patient_data_cleaned_with_age_category.xlsx")
    df["Patient Visit Date"] = pd.to_datetime(df["Patient Visit Date"])
    df["Year"]      = df["Patient Visit Date"].dt.year
    df["Month"]     = df["Patient Visit Date"].dt.month
    df["Quarter"]   = df["Patient Visit Date"].dt.quarter
    df["DayOfWeek"] = df["Patient Visit Date"].dt.day_name()
    df["Hour"]      = df["Patient Visit Date"].dt.hour
    df["Age Category"] = pd.Categorical(
        df["Age Category"],
        categories=["Children", "Youth", "Middle Age", "Senior Citizen"], ordered=True
    )
    def tw(h):
        s = (h // 3) * 3
        return f"{s:02d}:00-{s+3:02d}:00"
    df["Time Window"] = df["Hour"].apply(tw)
    return df

df = load_data()

MONTH_ABR = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
             7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}

# Add Month Name for user-friendly filtering
df["Month Name"] = df["Month"].map(MONTH_ABR)

# Chronological list of available months for multiselect options
ordered_months = [MONTH_ABR[i] for i in range(1, 13) if MONTH_ABR[i] in df["Month Name"].unique()]


# ── Plotly base ──────────────────────────────────────────────────────────────
def base_layout(fig, height=300, margin=None, **kwargs):
    m = margin or dict(l=8, r=8, t=28, b=8)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=m,
        **kwargs
    )

# ── Dual-axis periodic chart builder ────────────────────────────────────────
def make_periodic_chart(x_vals, bar_vals, pct_vals, bar_label, pct_label,
                        height=220, bar_textsize=11, pct_textsize=9,
                        xaxis_kwargs=None, showlegend=True):
    """
    Dual-axis bar+line chart.
    - Left Y: patient count bars (hidden tick labels, gridlines off)
    - Right Y: % change line, visible with % format, zero-line shown
    - First pct value forced to 0.00% (baseline period)
    """
    pct_display = pct_vals.copy()
    pct_display.iloc[0] = 0.0

    pct_texts = [f"{v:.2f}%" for v in pct_display]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=x_vals, y=bar_vals,
        marker_color=TEAL, name=bar_label,
        text=bar_vals, textposition='outside',
        textfont=dict(size=bar_textsize, color="#111111", family="Arial Black"),
        cliponaxis=False,
    ), secondary_y=False)

    n = len(pct_display)
    textpos = ['top center' if i % 2 == 0 else 'bottom center' for i in range(n)]

    fig.add_trace(go.Scatter(
        x=x_vals, y=pct_display,
        mode='lines+markers+text', name=pct_label,
        line=dict(color=LINE_CLR, width=2.5),
        marker=dict(size=8, color=LINE_CLR),
        text=pct_texts,
        textposition=textpos,
        textfont=dict(size=pct_textsize, color="#111111", family="Arial Black"),
        cliponaxis=False,
    ), secondary_y=True)

    xkw = xaxis_kwargs or {}
    xaxis_final = dict(tickfont=dict(size=10, color="#222222"))
    xaxis_final.update(xkw)
    base_layout(fig, height=height,
                showlegend=showlegend,
                legend=dict(orientation='h', y=1.20, x=0, font=dict(size=12, color="#111111")),
                xaxis=xaxis_final,
                yaxis=dict(visible=False, showgrid=False),
                yaxis2=dict(
                    tickformat=".1f",
                    ticksuffix="%",
                    tickfont=dict(size=10, color="#222222"),
                    showgrid=True,
                    gridcolor="rgba(100,100,100,0.15)",
                    zeroline=False,
                    side="right",
                ))
    return fig


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tabs = st.tabs(["📋 Summary", "📈 Periodic Movement",
                "🔬 Diagnosis vs Patients", "🎂 Diagnosis vs Age", "🕐 Patient Visits"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SUMMARY
# ════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    # Filters for Summary
    f1_yr, f1_mo = st.columns(2)
    with f1_yr:
        sel_yr1 = st.multiselect("Year", sorted(df['Year'].unique()), key="sum_yr")
    with f1_mo:
        sel_mo1 = st.multiselect("Month", ordered_months, key="sum_mo")
        
    df1 = df.copy()
    if sel_yr1: df1 = df1[df1['Year'].isin(sel_yr1)]
    if sel_mo1: df1 = df1[df1['Month Name'].isin(sel_mo1)]

    # Handle edge case where filters remove all data to avoid division by zero
    total_docs = df1['Doctor ID'].nunique()
    doc_ratio = f"{len(df1)/total_docs:.2f}" if total_docs > 0 else "0.00"
    avg_age = str(int(df1['Age'].mean())) if not df1.empty else "0"

    # KPI row 1 — 5 cards
    row1 = st.columns(5)
    kpis_r1 = [
        ("🧑‍⚕️ Total Patients",      f"{len(df1):,}"),
        ("🌍 Nationalities",          str(df1['Nationality'].nunique())),
        ("📅 Avg Patient Age",        avg_age),
        ("👨 Male Patients",          f"{(df1['Sex']=='Male').sum():,}"),
        ("👩 Female Patients",        f"{(df1['Sex']=='Female').sum():,}"),
    ]
    for col, (label, val) in zip(row1, kpis_r1):
        with col:
            st.metric(label=label, value=val, border=True)

    # KPI row 2 — 4 cards
    row2 = st.columns(4)
    kpis_r2 = [
        ("🏥 Total Hospitals",        str(df1['Hospital Name'].nunique())),
        ("👨‍⚕️ Total Doctors",         f"{total_docs:,}"),
        ("🩺 Diagnoses",              str(df1['Diagnosis Name'].nunique())),
        ("⚖️ Patient-Doctor Ratio",  doc_ratio),
    ]
    for col, (label, val) in zip(row2, kpis_r2):
        with col:
            st.metric(label=label, value=val, border=True)

    st.divider()

    # Bottom 4 panels
    col_map, col_hosp, col_sex, col_age = st.columns([2.4, 1.8, 1.1, 1.3])

    # ── Map ──
    COORDS = {
        "Bahrain":(26.07,50.56), "Cyprus":(35.13,33.43), "Egypt":(26.82,30.80),
        "Iran":(32.43,53.69), "Iraq":(33.22,43.68), "Jordan":(30.59,36.24),
        "Kuwait":(29.31,47.48), "Lebanon":(33.85,35.86), "Oman":(21.47,55.98),
        "Palestine":(31.95,35.23), "Qatar":(25.35,51.18), "Saudi Arabia":(23.89,45.08),
        "Syria":(34.80,38.00), "Turkey":(38.96,35.24),
        "United Arab Emirates":(23.42,53.85), "Yemen":(15.55,48.52),
    }
    nat = df1['Nationality'].value_counts().reset_index()
    nat.columns = ['Nationality','Count']
    nat['lat'] = nat['Nationality'].map(lambda x: COORDS.get(x, (0,0))[0])
    nat['lon'] = nat['Nationality'].map(lambda x: COORDS.get(x, (0,0))[1])

    if not nat.empty:
        max_count = nat['Count'].max()
        nat['size_scaled'] = (nat['Count'] / max_count) ** 0.5 * 18
        nat['size_scaled'] = nat['size_scaled'].clip(lower=5)

    with col_map:
        st.subheader("Patients by Nationality", anchor=False)
        fig_map = go.Figure(go.Scattermap(
            lat=nat['lat'] if not nat.empty else [],
            lon=nat['lon'] if not nat.empty else [],
            mode='markers',
            marker=go.scattermap.Marker(
                size=nat['size_scaled'] if not nat.empty else [],
                color=TEAL,
                opacity=0.8,
            ),
            text=nat['Nationality'] if not nat.empty else [],
            customdata=nat['Count'] if not nat.empty else [],
            hovertemplate="<b>%{text}</b><br>Patients: %{customdata}<extra></extra>",
        ))
        fig_map.update_layout(
            map=dict(
                style="carto-positron",
                center=dict(lat=28, lon=44),
                zoom=2.8,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig_map, width='stretch')

    # ── Hospital bar ──
    with col_hosp:
        st.subheader("Patients by Hospital", anchor=False)
        hosp = df1['Hospital Name'].value_counts().sort_values()
        fig_h = go.Figure(go.Bar(
            x=hosp.values, y=hosp.index, orientation='h',
            marker_color=TEAL,
            text=hosp.values, textposition='outside',
        ))
        base_layout(fig_h, height=300,
                    xaxis=dict(visible=False),
                    yaxis=dict(tickfont=dict(size=10, color="#222222"), side='right'),
                    bargap=0.2)
        st.plotly_chart(fig_h, width='stretch')

    # ── Sex donut ──
    with col_sex:
        st.subheader("Sex Ratio", anchor=False)
        sc = df1['Sex'].value_counts()
        fig_sex = go.Figure(go.Pie(
            labels=sc.index, values=sc.values, hole=0.52,
            marker=dict(colors=[TEAL, PINK]),
            textinfo='percent',
            textfont=dict(size=13, color="#111111"),
            insidetextorientation='horizontal',
        ))
        base_layout(fig_sex, height=300, margin=dict(l=8,r=8,t=28,b=60),
                    showlegend=True,
                    legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.12,
                                font=dict(size=12, color="#222222")))
        st.plotly_chart(fig_sex, width='stretch')

    # ── Age category donut ──
    with col_age:
        st.subheader("Age Category", anchor=False)
        ac = df1['Age Category'].value_counts()
        age_colors = ["#2196F3", TEAL, "#FF9800", "#F44336"]
        fig_age = go.Figure(go.Pie(
            labels=ac.index, values=ac.values, hole=0.52,
            marker=dict(colors=age_colors),
            textinfo='percent',
            textfont=dict(size=12, color="#111111"),
            insidetextorientation='horizontal',
        ))
        base_layout(fig_age, height=300, margin=dict(l=8,r=8,t=28,b=60),
                    showlegend=True,
                    legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.12,
                                font=dict(size=11, color="#222222")))
        st.plotly_chart(fig_age, width='stretch')


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — PERIODIC MOVEMENT (Unchanged)
# ════════════════════════════════════════════════════════════════════════════
with tabs[1]:

    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        sel_nat = st.multiselect("Nationality", sorted(df['Nationality'].unique()), key="pm_nat")
    with fc2:
        sel_age_cat = st.selectbox("Age Category", ["All"]+list(df['Age Category'].cat.categories), key="pm_age")
    with fc3:
        sel_hosp_pm = st.selectbox("Hospital", ["All"]+sorted(df['Hospital Name'].unique()), key="pm_hosp")
    with fc4:
        sel_diag_pm = st.selectbox("Diagnosis", ["All"]+sorted(df['Diagnosis Name'].unique()), key="pm_diag")

    dff = df.copy()
    if sel_nat:              dff = dff[dff['Nationality'].isin(sel_nat)]
    if sel_age_cat != "All": dff = dff[dff['Age Category'] == sel_age_cat]
    if sel_hosp_pm != "All": dff = dff[dff['Hospital Name'] == sel_hosp_pm]
    if sel_diag_pm != "All": dff = dff[dff['Diagnosis Name'] == sel_diag_pm]

    yearly    = dff.groupby('Year').size().reset_index(name='Patients')
    yearly['YoY%'] = yearly['Patients'].pct_change() * 100

    quarterly = dff.groupby(['Year','Quarter']).size().reset_index(name='Patients')
    quarterly['Label'] = quarterly.apply(lambda r: f"Q{int(r['Quarter'])} {int(r['Year'])}", axis=1)
    quarterly['QoQ%'] = quarterly['Patients'].pct_change() * 100

    monthly   = dff.groupby(['Year','Month']).size().reset_index(name='Patients')
    monthly['Label'] = monthly.apply(lambda r: f"{MONTH_ABR[r['Month']]} {r['Year']}", axis=1)
    monthly['MoM%'] = monthly['Patients'].pct_change() * 100

    rl, rr = st.columns(2)

    with rl:
        st.subheader("Yearly Movement", anchor=False)
        fig_y = make_periodic_chart(
            x_vals=yearly['Year'],
            bar_vals=yearly['Patients'],
            pct_vals=yearly['YoY%'].fillna(0),
            bar_label='Total Patients', pct_label='YoY%',
            height=260, bar_textsize=12, pct_textsize=10,
            xaxis_kwargs=dict(tickvals=yearly['Year'].tolist()),
            showlegend=True,
        )
        st.plotly_chart(fig_y, width='stretch')

    with rr:
        st.subheader("Quarterly Movement", anchor=False)
        fig_q = make_periodic_chart(
            x_vals=quarterly['Label'],
            bar_vals=quarterly['Patients'],
            pct_vals=quarterly['QoQ%'].fillna(0),
            bar_label='Total Patients', pct_label='QoQ%',
            height=260, bar_textsize=10, pct_textsize=9,
            xaxis_kwargs=dict(tickangle=45, tickfont=dict(size=8, color="#333333")),
            showlegend=True,
        )
        st.plotly_chart(fig_q, width='stretch')

    st.subheader("Monthly Movement", anchor=False)
    fig_m = make_periodic_chart(
        x_vals=monthly['Label'],
        bar_vals=monthly['Patients'],
        pct_vals=monthly['MoM%'].fillna(0),
        bar_label='Total Patients', pct_label='MoM%',
        height=320, bar_textsize=9, pct_textsize=8,
        xaxis_kwargs=dict(tickangle=45, tickfont=dict(size=8, color="#333333")),
        showlegend=True,
    )
    st.plotly_chart(fig_m, width='stretch')


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — DIAGNOSIS vs PATIENTS
# ════════════════════════════════════════════════════════════════════════════
with tabs[2]:

    fa1, fa2, fa3, fa4 = st.columns(4)
    with fa1:
        sel_nat3 = st.multiselect("Nationality", sorted(df['Nationality'].unique()), key="dp_nat")
    with fa2:
        sel_yr3 = st.multiselect("Year", sorted(df['Year'].unique()), key="dp_yr")
    with fa3:
        sel_mo3 = st.multiselect("Month", ordered_months, key="dp_mo")
    with fa4:
        sel_hosp3 = st.selectbox("Hospital", ["All"]+sorted(df['Hospital Name'].unique()), key="dp_hosp")

    dfd = df.copy()
    if sel_nat3:             dfd = dfd[dfd['Nationality'].isin(sel_nat3)]
    if sel_yr3:              dfd = dfd[dfd['Year'].isin(sel_yr3)]
    if sel_mo3:              dfd = dfd[dfd['Month Name'].isin(sel_mo3)]
    if sel_hosp3 != "All":  dfd = dfd[dfd['Hospital Name'] == sel_hosp3]

    diag_counts = dfd['Diagnosis Name'].value_counts().sort_index()

    st.subheader("Patients by Diagnosis", anchor=False)
    fig_dp = go.Figure(go.Bar(
        x=diag_counts.index, y=diag_counts.values,
        marker_color=TEAL,
        text=diag_counts.values, textposition='outside',
        textfont=dict(size=12, color="#111111", family="Arial Black"),
        cliponaxis=False,
    ))
    base_layout(fig_dp, height=420,
                xaxis=dict(tickangle=45, tickfont=dict(size=10, color="#333333")),
                yaxis=dict(visible=False), bargap=0.2)
    st.plotly_chart(fig_dp, width='stretch')

    if not diag_counts.empty:
        max_d = diag_counts.idxmax(); max_v = diag_counts.max()
        min_d = diag_counts.idxmin(); min_v = diag_counts.min()
        st.info(f"Highest: **{max_d}** with **{max_v}** patients. "
                f"Lowest: **{min_d}** with **{min_v}** patients.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — DIAGNOSIS vs AGE
# ════════════════════════════════════════════════════════════════════════════
with tabs[3]:

    fb1, fb2, fb3, fb4 = st.columns(4)
    with fb1:
        sel_nat4 = st.multiselect("Nationality", sorted(df['Nationality'].unique()), key="da_nat")
    with fb2:
        sel_yr4 = st.multiselect("Year", sorted(df['Year'].unique()), key="da_yr")
    with fb3:
        sel_mo4 = st.multiselect("Month", ordered_months, key="da_mo")
    with fb4:
        sel_hosp4 = st.selectbox("Hospital", ["All"]+sorted(df['Hospital Name'].unique()), key="da_hosp")

    dfda = df.copy()
    if sel_nat4:             dfda = dfda[dfda['Nationality'].isin(sel_nat4)]
    if sel_yr4:              dfda = dfda[dfda['Year'].isin(sel_yr4)]
    if sel_mo4:              dfda = dfda[dfda['Month Name'].isin(sel_mo4)]
    if sel_hosp4 != "All":  dfda = dfda[dfda['Hospital Name'] == sel_hosp4]

    avg_age_diag = dfda.groupby('Diagnosis Name')['Age'].mean().round(0).astype(float)
    # Filter out NaNs if any diagnosis had no patients
    avg_age_diag = avg_age_diag.dropna().astype(int).sort_index()

    st.subheader("Average Age by Diagnosis", anchor=False)
    fig_da = go.Figure(go.Bar(
        x=avg_age_diag.index, y=avg_age_diag.values,
        marker_color=TEAL,
        text=avg_age_diag.values, textposition='outside',
        textfont=dict(size=12, color="#111111", family="Arial Black"),
        cliponaxis=False,
    ))
    max_val = avg_age_diag.max() + 10 if not avg_age_diag.empty else 100
    base_layout(fig_da, height=420,
                xaxis=dict(tickangle=45, tickfont=dict(size=10, color="#333333")),
                yaxis=dict(range=[0, max_val], visible=False),
                bargap=0.2)
    st.plotly_chart(fig_da, width='stretch')

    if not avg_age_diag.empty:
        hi_diag = avg_age_diag.idxmax(); hi_age = avg_age_diag.max()
        lo_diag = avg_age_diag.idxmin(); lo_age = avg_age_diag.min()
        st.info(f"Age range across diagnoses: **{lo_age}** (**{lo_diag}**) to **{hi_age}** (**{hi_diag}**).")


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — PATIENT VISITS
# ════════════════════════════════════════════════════════════════════════════
with tabs[4]:

    fv1, fv2, fv3, fv4 = st.columns(4)
    with fv1:
        sel_nat5 = st.multiselect("Nationality", sorted(df['Nationality'].unique()), key="pv_nat")
    with fv2:
        sel_yr5 = st.multiselect("Year", sorted(df['Year'].unique()), key="pv_yr")
    with fv3:
        sel_mo5 = st.multiselect("Month", ordered_months, key="pv_mo")
    with fv4:
        sel_hosp5 = st.selectbox("Hospital", ["All"]+sorted(df['Hospital Name'].unique()), key="pv_hosp")

    dfv = df.copy()
    if sel_nat5:             dfv = dfv[dfv['Nationality'].isin(sel_nat5)]
    if sel_yr5:              dfv = dfv[dfv['Year'].isin(sel_yr5)]
    if sel_mo5:              dfv = dfv[dfv['Month Name'].isin(sel_mo5)]
    if sel_hosp5 != "All":  dfv = dfv[dfv['Hospital Name'] == sel_hosp5]

    day_order = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    visits_day = dfv['DayOfWeek'].value_counts().reindex(day_order).reset_index()
    visits_day.columns = ['Day','Patients']
    visits_day['Patients'] = visits_day['Patients'].fillna(0)

    tw_order = [f"{s:02d}:00-{s+3:02d}:00" for s in range(0,24,3)]
    tw_sex = dfv.groupby(['Time Window','Sex']).size().reset_index(name='Patients')
    tw_sex['Time Window'] = pd.Categorical(tw_sex['Time Window'], categories=tw_order, ordered=True)
    tw_sex = tw_sex.sort_values('Time Window')

    lv, rv = st.columns(2)

    with lv:
        st.subheader("Patients Visit by Day", anchor=False)
        fig_day = go.Figure(go.Scatter(
            x=visits_day['Day'], y=visits_day['Patients'],
            mode='lines+markers+text',
            fill='tozeroy', fillcolor="rgba(0,176,160,0.2)",
            line=dict(color=TEAL, width=2.5),
            marker=dict(size=8, color=TEAL),
            text=visits_day['Patients'],
            textposition='top center',
            textfont=dict(size=11, family='Arial Black'),
        ))
        base_layout(fig_day, height=300,
                    xaxis=dict(tickfont=dict(size=11, color="#222222")),
                    yaxis=dict(visible=False))
        st.plotly_chart(fig_day, width='stretch')

        if not visits_day['Patients'].sum() == 0:
            mx_d = visits_day.loc[visits_day['Patients'].idxmax()]
            mn_d = visits_day.loc[visits_day['Patients'].idxmin()]
            pct  = (mx_d['Patients'] - mn_d['Patients']) / mn_d['Patients'] * 100 if mn_d['Patients'] > 0 else 0
            st.info(
                f"At **{int(mx_d['Patients']):,}**, **{mx_d['Day']}** had the highest visits — "
                f"**{pct:.2f}%** higher than **{mn_d['Day']}** ({int(mn_d['Patients']):,})."
            )

    with rv:
        st.subheader("Patients Visit by Time Window & Sex", anchor=False)
        female_tw = tw_sex[tw_sex['Sex'] == 'Female']
        male_tw   = tw_sex[tw_sex['Sex'] == 'Male']

        fig_tw = go.Figure()
        fig_tw.add_trace(go.Scatter(
            x=female_tw['Time Window'], y=female_tw['Patients'],
            mode='lines+markers+text', name='Female',
            line=dict(color=PINK, width=2), marker=dict(size=6, color=PINK),
            text=female_tw['Patients'], textposition='top center',
            textfont=dict(size=9, color=PINK),
        ))
        fig_tw.add_trace(go.Scatter(
            x=male_tw['Time Window'], y=male_tw['Patients'],
            mode='lines+markers+text', name='Male',
            line=dict(color=TEAL, width=2), marker=dict(size=6, color=TEAL),
            text=male_tw['Patients'], textposition='bottom center',
            textfont=dict(size=9, color=TEAL),
        ))
        base_layout(fig_tw, height=300,
                    xaxis=dict(tickfont=dict(size=9, color="#222222"), tickangle=30),
                    yaxis=dict(visible=False),
                    showlegend=True,
                    legend=dict(orientation='h', x=0.5, xanchor='center',
                                y=1.12, font=dict(size=12, color="#111111")))
        st.plotly_chart(fig_tw, width='stretch')

        if not female_tw.empty and not male_tw.empty:
            avg_f = female_tw['Patients'].mean()
            avg_m = male_tw['Patients'].mean()
            higher = "Female" if avg_f > avg_m else "Male"
            lower  = "Male"   if avg_f > avg_m else "Female"
            hi_val = max(avg_f, avg_m); lo_val = min(avg_f, avg_m)
            merged = female_tw.set_index('Time Window')['Patients'].subtract(
                male_tw.set_index('Time Window')['Patients'], fill_value=0)
            max_win = merged.abs().idxmax()
            max_gap = abs(int(merged[max_win]))
            gap_hi  = "Male" if merged[max_win] < 0 else "Female"
            st.info(
                f"Average visits higher for **{higher}** ({hi_val:.1f}) than {lower} ({lo_val:.1f}). "
                f"Biggest gap at **{max_win}** — **{gap_hi}** led by **{max_gap}**."
            )