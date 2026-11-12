from flask import Flask, request, render_template, session

app = Flask(__name__)
app.secret_key = "lab-only-secret-key"

import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="sqlilab_db",
        user="sqlilab_user",
        password="LabPass123!",
        host="localhost"
    )

@app.route("/")
def home():
    return '<a href="/login">Go to login</a>'

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ FIXED — parameterized query using %s placeholders.
    # psycopg2 sends the query structure and the user's data as two
    # SEPARATE things to PostgreSQL. No matter what characters the user
    # types, it is always treated as pure data — it can never change
    # the structure of the SQL command itself.
    query = "SELECT id, username, role FROM users WHERE username = %s AND password = %s"
    cur.execute(query, (username, password))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        session["user_id"] = user[0]
        session["username"] = user[1]
        session["role"] = user[2]
        return f"<h2>Welcome, {user[1]}! Your role is: {user[2]}</h2>"
    else:
        return render_template("login.html", error="Invalid credentials")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
