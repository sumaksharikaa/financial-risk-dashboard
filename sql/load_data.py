import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import numpy as np

DB_NAME   = "lending_risk"
DB_USER   = ""
DB_HOST   = "localhost"
DB_PORT   = 5432
CSV_PATH  = "data/loan_data.csv"
CHUNKSIZE = 10_000

def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER or None,
        host=DB_HOST, port=DB_PORT
    )

def clean(val):
    if val is None:
        return None
    if isinstance(val, float) and np.isnan(val):
        return None
    try:
        if pd.isna(val):
            return None
    except:
        pass
    return val

def parse_rate(val):
    try:
        if pd.isna(val):
            return None
        return float(str(val).replace('%', '').strip())
    except:
        return None

def parse_term(val):
    try:
        if pd.isna(val):
            return None
        return int(str(val).strip().split()[0])
    except:
        return None

print("Connecting to database...")
conn = get_conn()
cur  = conn.cursor()

print(f"Reading CSV in chunks of {CHUNKSIZE:,} rows...")
reader = pd.read_csv(
    CSV_PATH,
    low_memory=False,
    chunksize=CHUNKSIZE,
    parse_dates=["issue_d", "earliest_cr_line"]
)

total_rows = 0
skipped    = 0

for chunk_num, chunk in enumerate(reader):
    chunk.columns = chunk.columns.str.strip()

    # Skip junk/summary rows — real loans always have a numeric loan_amnt
    chunk = chunk[pd.to_numeric(chunk["loan_amnt"], errors="coerce").notna()]
    chunk = chunk[pd.to_numeric(chunk["id"], errors="coerce").notna()]

    if chunk.empty:
        continue

    borrower_rows = []
    for _, row in chunk.iterrows():
        borrower_rows.append((
            clean(row.get("member_id")) or f"B-{row.name}",
            clean(row.get("annual_inc")),
            clean(row.get("verification_status")),
            clean(row.get("emp_length")),
            clean(row.get("home_ownership")),
            clean(row.get("addr_state")),
            row.get("earliest_cr_line") if not pd.isna(row.get("earliest_cr_line", float("nan"))) else None,
        ))

    execute_values(cur, """
        INSERT INTO borrowers
            (borrower_id, annual_income, income_verified,
             employment_length, home_ownership, addr_state, earliest_credit_line)
        VALUES %s
        ON CONFLICT (borrower_id) DO NOTHING
    """, borrower_rows)

    loan_rows = []
    for _, row in chunk.iterrows():
        loan_rows.append((
            str(clean(row.get("id"))),
            clean(row.get("member_id")) or f"B-{row.name}",
            clean(row.get("loan_amnt")),
            clean(row.get("funded_amnt")),
            parse_term(row.get("term")),
            parse_rate(row.get("int_rate")),
            clean(row.get("installment")),
            clean(row.get("grade")),
            clean(row.get("sub_grade")),
            clean(row.get("purpose")),
            row.get("issue_d") if not pd.isna(row.get("issue_d", float("nan"))) else None,
            clean(row.get("dti")),
            clean(row.get("fico_range_low")),
            clean(row.get("fico_range_high")),
            clean(row.get("open_acc")),
            clean(row.get("total_acc")),
            clean(row.get("delinq_2yrs")),
            clean(row.get("pub_rec")),
            parse_rate(row.get("revol_util")),
            clean(row.get("loan_status")),
        ))

    execute_values(cur, """
        INSERT INTO loans
            (loan_id, borrower_id, loan_amount, funded_amount, term,
             int_rate, installment, grade, sub_grade, purpose, issue_date,
             dti, fico_range_low, fico_range_high, open_accounts, total_accounts,
             delinq_2yrs, pub_rec, revol_util, loan_status)
        VALUES %s
        ON CONFLICT (loan_id) DO NOTHING
    """, loan_rows)

    conn.commit()
    total_rows += len(chunk)
    print(f"  Chunk {chunk_num + 1}: {total_rows:,} rows loaded so far...")

cur.close()
conn.close()
print(f"\nDone. {total_rows:,} total rows loaded into lending_risk.")
