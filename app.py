import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Financial Risk Dashboard",
    page_icon="💳",
    layout="wide"
)

@st.cache_data
def load_data():
    cols = ['grade','loan_amnt','int_rate','dti','fico_range_low',
            'purpose','term','loan_status','issue_d',
            'annual_inc','home_ownership','addr_state',
            'fico_range_high','delinq_2yrs','revol_util']
    df = pd.read_csv('data/loan_sample.csv', usecols=cols, low_memory=False)
    df = df[pd.to_numeric(df['loan_amnt'], errors='coerce').notna()]
    df.rename(columns={'loan_amnt':'loan_amount','annual_inc':'annual_income',
                       'issue_d':'issue_date'}, inplace=True)
    df['int_rate'] = df['int_rate'].astype(str).str.replace('%','').astype(float, errors='ignore')
    df['term'] = df['term'].astype(str).str.strip().str.split().str[0]
    df['default_flag'] = df['loan_status'].isin(
        ['Charged Off','Default',
         'Does not meet the credit policy. Status:Charged Off']).astype(int)
    df['issue_date'] = pd.to_datetime(df['issue_date'], format='%b-%Y', errors='coerce')
    return df.dropna(subset=['grade','loan_amount'])

st.title("💳 Financial Risk Dashboard")
st.markdown("


cat > ~/financial-risk-dashboard/app.py << 'EOF'
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Financial Risk Dashboard",
    page_icon="💳",
    layout="wide"
)

@st.cache_data
def load_data():
    cols = ['grade','loan_amnt','int_rate','dti','fico_range_low',
            'purpose','term','loan_status','issue_d',
            'annual_inc','home_ownership','addr_state',
            'fico_range_high','delinq_2yrs','revol_util']
    df = pd.read_csv('data/loan_sample.csv', usecols=cols, low_memory=False)
    df = df[pd.to_numeric(df['loan_amnt'], errors='coerce').notna()]
    df.rename(columns={'loan_amnt':'loan_amount','annual_inc':'annual_income',
                       'issue_d':'issue_date'}, inplace=True)
    df['int_rate'] = df['int_rate'].astype(str).str.replace('%','').astype(float, errors='ignore')
    df['term'] = df['term'].astype(str).str.strip().str.split().str[0]
    df['default_flag'] = df['loan_status'].isin(
        ['Charged Off','Default',
         'Does not meet the credit policy. Status:Charged Off']).astype(int)
    df['issue_date'] = pd.to_datetime(df['issue_date'], format='%b-%Y', errors='coerce')
    return df.dropna(subset=['grade','loan_amount'])

st.title("💳 Financial Risk Dashboard")
st.markdown("**Lending Club Loan Portfolio — 2007 to 2018**")

with st.spinner("Loading 2.26M loan records..."):
    df = load_data()

# ── KPI CARDS ──────────────────────────────────────────────
st.subheader("Portfolio Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Loans", f"{len(df):,}")
col2.metric("Total Volume", f"${df['loan_amount'].sum()/1e9:.1f}B")
col3.metric("Avg Interest Rate", f"{pd.to_numeric(df['int_rate'], errors='coerce').mean():.2f}%")
col4.metric("Overall Default Rate", f"{df['default_flag'].mean()*100:.2f}%")

st.divider()

# ── SIDEBAR FILTERS ────────────────────────────────────────
st.sidebar.header("Filters")
grades = st.sidebar.multiselect(
    "Loan Grade", options=sorted(df['grade'].dropna().unique()),
    default=sorted(df['grade'].dropna().unique())
)
terms = st.sidebar.multiselect(
    "Loan Term (months)", options=sorted(df['term'].dropna().unique()),
    default=sorted(df['term'].dropna().unique())
)

df_filtered = df[df['grade'].isin(grades) & df['term'].isin(terms)]

# ── ROW 1: GRADE ANALYSIS ──────────────────────────────────
st.subheader("Default Rate by Loan Grade")
col1, col2 = st.columns(2)

grade_stats = df_filtered.groupby('grade').agg(
    total=('default_flag','count'),
    defaults=('default_flag','sum'),
    avg_int_rate=('int_rate','mean')
).reset_index()
grade_stats['default_rate'] = grade_stats['defaults'] / grade_stats['total'] * 100

with col1:
    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(grade_stats['grade'], grade_stats['default_rate'],
           color=sns.color_palette('RdYlGn_r', len(grade_stats)))
    ax.set_title('Default Rate by Grade', fontweight='bold')
    ax.set_xlabel('Grade'); ax.set_ylabel('Default Rate (%)')
    for i, v in enumerate(grade_stats['default_rate']):
        ax.text(i, v+0.3, f'{v:.1f}%', ha='center', fontsize=9)
    st.pyplot(fig); plt.close()

with col2:
    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(grade_stats['grade'], grade_stats['avg_int_rate'],
           color=sns.color_palette('Blues', len(grade_stats)))
    ax.set_title('Avg Interest Rate by Grade', fontweight='bold')
    ax.set_xlabel('Grade'); ax.set_ylabel('Interest Rate (%)')
    st.pyplot(fig); plt.close()

st.divider()

# ── ROW 2: PURPOSE + FICO ──────────────────────────────────
st.subheader("Risk by Loan Purpose and FICO Score")
col1, col2 = st.columns(2)

with col1:
    purpose_stats = df_filtered.groupby('purpose').agg(
        total=('default_flag','count'),
        default_rate=('default_flag','mean')
    ).reset_index()
    purpose_stats['default_rate'] *= 100
    purpose_stats = purpose_stats[purpose_stats['total']>500].sort_values('default_rate')
    fig, ax = plt.subplots(figsize=(7,5))
    ax.barh(purpose_stats['purpose'], purpose_stats['default_rate'],
            color=sns.color_palette('RdYlGn_r', len(purpose_stats)))
    ax.set_title('Default Rate by Purpose', fontweight='bold')
    ax.set_xlabel('Default Rate (%)')
    st.pyplot(fig); plt.close()

with col2:
    df_f2 = df_filtered.copy()
    df_f2['fico_band'] = pd.cut(df_f2['fico_range_low'],
        bins=[0,649,699,749,799,850],
        labels=['<650','650-699','700-749','750-799','800+'])
    fico_stats = df_f2.groupby('fico_band')['default_flag'].mean() * 100
    fig, ax = plt.subplots(figsize=(7,5))
    ax.bar(fico_stats.index.astype(str), fico_stats.values,
           color=sns.color_palette('RdYlGn', len(fico_stats)))
    ax.set_title('Default Rate by FICO Band', fontweight='bold')
    ax.set_xlabel('FICO Score Band'); ax.set_ylabel('Default Rate (%)')
    for i, v in enumerate(fico_stats.values):
        ax.text(i, v+0.2, f'{v:.1f}%', ha='center', fontsize=9)
    st.pyplot(fig); plt.close()

st.divider()

# ── ROW 3: TIME SERIES ─────────────────────────────────────
st.subheader("Monthly Loan Origination Volume")
monthly = df_filtered.groupby(df_filtered['issue_date'].dt.to_period('M')).agg(
    volume=('loan_amount','sum'),
    default_rate=('default_flag','mean')
).reset_index()
monthly['issue_date'] = monthly['issue_date'].astype(str)

fig, ax1 = plt.subplots(figsize=(14,4))
ax1.fill_between(range(len(monthly)), monthly['volume']/1e6, alpha=0.4, color='steelblue')
ax1.plot(range(len(monthly)), monthly['volume']/1e6, color='steelblue', lw=2)
ax1.set_ylabel('Loan Volume ($M)', color='steelblue')
ax1.set_xticks(range(0, len(monthly), 12))
ax1.set_xticklabels(monthly['issue_date'].iloc[::12], rotation=45, fontsize=8)
ax2 = ax1.twinx()
ax2.plot(range(len(monthly)), monthly['default_rate']*100,
         color='crimson', lw=2, linestyle='--')
ax2.set_ylabel('Default Rate (%)', color='crimson')
ax1.set_title('Monthly Volume and Default Rate Trend', fontweight='bold')
st.pyplot(fig); plt.close()

st.divider()

st.subheader("Loan Data Explorer")
st.dataframe(
    df_filtered[['grade','loan_amount','int_rate','dti',
                 'fico_range_low','purpose','loan_status','default_flag']]
    .head(1000), use_container_width=True
)

st.caption("Data source: Lending Club (2007–2018) | Built by Sumaksharika")
