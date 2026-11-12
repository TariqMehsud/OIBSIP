import psycopg2

conn = psycopg2.connect(
    dbname="sqlilab_db",
    user="sqlilab_user",
    password="LabPass123!",
    host="localhost"
)
cur = conn.cursor()

# Drop tables if they exist, so this script is re-runnable
cur.execute("DROP TABLE IF EXISTS admin_secrets, orders, users CASCADE;")

# Users table — this is what we'll attack
cur.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        role VARCHAR(20) DEFAULT 'user'
    );
""")

# Orders table — gives us something extra to enumerate via UNION
cur.execute("""
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        item VARCHAR(100),
        amount NUMERIC(10,2)
    );
""")

# A "secrets" table — simulates sensitive data an attacker shouldn't reach
cur.execute("""
    CREATE TABLE admin_secrets (
        id SERIAL PRIMARY KEY,
        secret_key VARCHAR(100),
        api_token VARCHAR(100)
    );
""")

# Seed data. Passwords are plaintext ON PURPOSE for this lab — never do this in real life.
cur.execute("""
    INSERT INTO users (username, password, email, role) VALUES
    ('alice', 'alicepass123', 'alice@example.com', 'user'),
    ('bob', 'bobpass456', 'bob@example.com', 'user'),
    ('admin', 'SuperSecretAdminPass!', 'admin@example.com', 'admin');
""")

cur.execute("""
    INSERT INTO orders (user_id, item, amount) VALUES
    (1, 'Laptop', 1200.00),
    (1, 'Mouse', 25.50),
    (2, 'Keyboard', 75.00);
""")

cur.execute("""
    INSERT INTO admin_secrets (secret_key, api_token) VALUES
    ('prod_db_master_key', 'sk_live_51Hx9aK2...FAKE_TOKEN');
""")

conn.commit()
cur.close()
conn.close()
print("Database seeded successfully.")
