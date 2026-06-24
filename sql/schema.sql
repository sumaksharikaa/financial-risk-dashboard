DROP TABLE IF EXISTS loan_payments;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS borrowers;

CREATE TABLE borrowers (
    borrower_id         VARCHAR(50)     PRIMARY KEY,
    annual_income       DECIMAL(12, 2),
    income_verified     VARCHAR(50),
    employment_length   VARCHAR(20),
    home_ownership      VARCHAR(20),
    addr_state          CHAR(2),
    earliest_credit_line DATE,
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loans (
    loan_id             VARCHAR(50)     PRIMARY KEY,
    borrower_id         VARCHAR(50)     NOT NULL REFERENCES borrowers(borrower_id),
    loan_amount         DECIMAL(12, 2)  NOT NULL,
    funded_amount       DECIMAL(12, 2),
    term                SMALLINT,
    int_rate            DECIMAL(5, 2),
    installment         DECIMAL(10, 2),
    grade               CHAR(1),
    sub_grade           VARCHAR(3),
    purpose             VARCHAR(100),
    issue_date          DATE,
    dti                 DECIMAL(6, 2),
    fico_range_low      SMALLINT,
    fico_range_high     SMALLINT,
    open_accounts       SMALLINT,
    total_accounts      SMALLINT,
    delinq_2yrs         SMALLINT,
    pub_rec             SMALLINT,
    revol_util          DECIMAL(5, 2),
    loan_status         VARCHAR(100),
    default_flag        SMALLINT GENERATED ALWAYS AS (
        CASE WHEN loan_status IN ('Charged Off', 'Default',
             'Does not meet the credit policy. Status:Charged Off') THEN 1 ELSE 0 END
    ) STORED,
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loan_payments (
    payment_id          SERIAL          PRIMARY KEY,
    loan_id             VARCHAR(50)     NOT NULL REFERENCES loans(loan_id),
    payment_date        DATE            NOT NULL,
    amount_paid         DECIMAL(10, 2),
    principal_paid      DECIMAL(10, 2),
    interest_paid       DECIMAL(10, 2),
    late_fee            DECIMAL(8, 2)   DEFAULT 0,
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loans_grade      ON loans(grade);
CREATE INDEX idx_loans_status     ON loans(loan_status);
CREATE INDEX idx_loans_issue_date ON loans(issue_date);
CREATE INDEX idx_loans_borrower   ON loans(borrower_id);
CREATE INDEX idx_payments_loan    ON loan_payments(loan_id);
CREATE INDEX idx_payments_date    ON loan_payments(payment_date);
CREATE INDEX idx_borrowers_state  ON borrowers(addr_state);
