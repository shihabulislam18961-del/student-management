
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import time

app = Flask(__name__)

DB_CONFIG = {
    "host": "mysql",
    "user": "student",
    "password": "student123",
    "database": "students"
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    # MySQL may need time to start before Flask connects.
    for attempt in range(30):
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    department VARCHAR(255) NOT NULL,
                    semester VARCHAR(100) NOT NULL
                )
            """)

            conn.commit()
            cursor.close()
            conn.close()
            print("MySQL connected; students table is ready.")
            return

        except mysql.connector.Error as error:
            print(f"MySQL connection attempt {attempt + 1}/30 failed: {error}")
            time.sleep(2)

    raise RuntimeError("Could not connect to MySQL after 30 attempts.")


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if search:
        pattern = f"%{search}%"
        cursor.execute("""
            SELECT * FROM students
            WHERE name LIKE %s
               OR email LIKE %s
               OR department LIKE %s
               OR phone LIKE %s
            ORDER BY id DESC
        """, (pattern, pattern, pattern, pattern))
    else:
        cursor.execute("SELECT * FROM students ORDER BY id DESC")

    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        students=students,
        search=search
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    department = request.form.get("department", "").strip()
    semester = request.form.get("semester", "").strip()

    if not all([name, email, phone, department, semester]):
        return "All student fields are required.", 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (name, email, phone, department, semester)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, phone, department, semester))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:id>", methods=["POST"])
def edit_student(id):
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    department = request.form.get("department", "").strip()
    semester = request.form.get("semester", "").strip()

    if not all([name, email, phone, department, semester]):
        return "All student fields are required.", 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET name = %s,
            email = %s,
            phone = %s,
            department = %s,
            semester = %s
        WHERE id = %s
    """, (name, email, phone, department, semester, id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = %s", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
