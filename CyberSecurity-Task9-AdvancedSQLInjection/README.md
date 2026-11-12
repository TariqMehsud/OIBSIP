# Advanced SQL Injection — Flask + PostgreSQL Vulnerable Login

**Track:** Cyber Security — Oasis Infobyte SIP
**Task:** Task 9 — Advanced SQL Injection (Exploit a SQL Injection Vulnerability)

## Executive Summary (for non-technical readers)

This project demonstrates how a common coding mistake in a web application's login
page can let an attacker read an entire database — usernames, passwords, and other
sensitive records — without ever knowing a valid password.

A small, intentionally vulnerable login application was built from scratch using
Python (Flask) and PostgreSQL. The vulnerability was then exploited step by step,
first manually and then verified using an industry-standard automated tool
(sqlmap), to show exactly how an attacker would discover and abuse this flaw in
a real system. Finally, the vulnerability was fixed, and the fix was proven to
work against the same attack payloads that succeeded before.

**Business risk:** An application with this flaw could expose all customer data,
credentials, and internal records to any attacker who finds the vulnerable input
field — no special access or insider knowledge required. The fix is simple,
well-documented, and should be applied to any application built with similar
database query patterns.

## Project Architecture

- **Database:** PostgreSQL (`sqlilab_db`), dedicated user (`sqlilab_user`)
- **Backend:** Python Flask (`app.py`)
- **Driver:** psycopg2
- Tables: `users`, `orders`, `admin_secrets` (seeded via `seed_db.py`)

## The Vulnerability

The login route built its SQL query by directly concatenating user input into
a query string:

```python
query = "SELECT id, username, role FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
```

Because user input and SQL code were never separated, an attacker could submit
input that changes the structure of the query itself.

## Exploitation Summary

Full payload-by-payload details and raw query outputs are in `exploitation_log.md`.

| # | Technique | Payload | Result |
|---|-----------|---------|--------|
| 1 | Authentication bypass | `' OR '1'='1' --` | Logged in without valid password |
| 2 | Column count discovery | `' UNION SELECT NULL,NULL,NULL --` | Confirmed 3-column query |
| 3 | Table enumeration | `UNION SELECT ... information_schema.tables` | Extracted all table names |
| 4 | Column enumeration | `UNION SELECT ... information_schema.columns` | Extracted `users` table schema |
| 5 | Data exfiltration | `UNION SELECT ... string_agg(username\|\|':'\|\|password)` | Dumped all usernames/passwords |
| 6 | Secondary table dump | Same technique vs. `admin_secrets` | Extracted fake API credentials |

### Automated Verification (sqlmap)

```bash
sqlmap -u "http://localhost:5000/login" --data="username=test&password=test" --dbms=postgresql --batch
```

sqlmap independently confirmed the `username` parameter is injectable via **4
distinct techniques**: error-based, stacked queries, time-based blind, and
UNION-based (matching the manual finding). Notably, sqlmap found **stacked
query injection**, which was not tested manually — this technique could allow
an attacker to execute arbitrary additional SQL statements (e.g., `DROP TABLE`,
`UPDATE`), not just read data.

## Remediation

The fix (`fixed_app.py`) replaces string concatenation with a parameterized
query:

```python
query = "SELECT id, username, role FROM users WHERE username = %s AND password = %s"
cur.execute(query, (username, password))
```

**Why this works:** psycopg2 sends the query structure and the user's input as
two separate components to PostgreSQL. The database always treats the input as
literal data, regardless of its content — it is structurally impossible for
user input to alter the query's logic.

**Verification:** The `' OR '1'='1' --` payload was re-tested against
`fixed_app.py` and correctly returned "Invalid credentials" instead of
bypassing authentication.

## Setup Instructions

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask psycopg2-binary

# Create a PostgreSQL database and user matching the credentials in app.py
sudo -u postgres psql
# CREATE USER sqlilab_user WITH PASSWORD 'LabPass123!';
# CREATE DATABASE sqlilab_db OWNER sqlilab_user;

python3 seed_db.py      # seeds sample data
python3 app.py           # runs the VULNERABLE version
python3 fixed_app.py     # runs the FIXED version
```

## Ethical Note

This project was built and tested exclusively against a local, self-hosted
application created for this exercise. No external systems, networks, or
third-party applications were accessed or tested.

## Files

- `app.py` — vulnerable Flask application
- `fixed_app.py` — remediated version using parameterized queries
- `seed_db.py` — database seeding script
- `exploitation_log.md` — full payload-by-payload exploitation log
- `templates/login.html` — login page template