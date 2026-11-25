from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_db_connection
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "contact-demo-secret-key")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO contacts (name, email, phone, message)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (name, email, phone, message))
        connection.commit()

        cursor.close()
        connection.close()

        flash("Message sent successfully!", "success")

        return redirect(url_for("contact"))

    return render_template("contact.html", success="Message sent successfully!")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM users
            WHERE username = %s AND password = %s
        """

        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid username or password"
        )

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("admin_login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, email, phone, message, created_at
        FROM contacts
        ORDER BY id DESC
    """)

    contacts = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        contacts=contacts
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)