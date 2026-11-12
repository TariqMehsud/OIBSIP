from flask import Flask, request, render_template, session, redirect

app = Flask(__name__)
app.secret_key = "lab-only-secret-key"  # fine for a local lab, never in real apps

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

    # ⚠️ VULNERABLE LINE — raw string concatenation builds the SQL query.
    # Anything the user types in `username` or `password` gets pasted
    # directly into the SQL string, so user input can change the
    # STRUCTURE of the query itself, not just its data.
    query = "SELECT id, username, role FROM users WHERE username = '" + username + "' AND password = '" + password + "'"

    print("Executing query:", query)  # so you can see the injected query in your terminal — great for your demo video

    try:
        cur.execute(query)
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        conn.close()
        return render_template("login.html", error=f"DB error: {e}")

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
