"""
RVM Backend - User Detail Capture Web App
-------------------------------------------
Serves a simple form (Name + Email) that opens automatically in the
browser whenever a user scans a code on the Reverse Vending Machine.

Run:
    ros2 run api_gateway web_form

Then either open http://localhost:5000/?session_id=<scan_code>
manually, or run the scan_listener node to auto-launch it on a real scan.
"""

from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import os
from datetime import datetime


def _template_folder():
    """Templates install to share/api_gateway/templates. Fall back to the
    source tree so `python app.py` still works outside a built workspace."""
    try:
        from ament_index_python.packages import get_package_share_directory
        return os.path.join(get_package_share_directory("api_gateway"), "templates")
    except Exception:
        return os.path.join(os.path.dirname(__file__), os.pardir, "templates")


app = Flask(__name__, template_folder=_template_folder())

DB_PATH = os.path.join(os.path.dirname(__file__), "rvm_users.db")


def init_db():
    """Create the users table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def index():
    """
    Shown when the scanner triggers the browser to open.
    session_id ties this form submission back to the specific
    scan/session on the machine (e.g. barcode value or a generated UUID).
    """
    session_id = request.args.get("session_id", "")
    return render_template("index.html", session_id=session_id)


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    session_id = request.form.get("session_id", "").strip()

    # Basic server-side validation
    if not name or not email or "@" not in email:
        return render_template(
            "index.html",
            session_id=session_id,
            error="Please enter a valid name and email address."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO users (session_id, name, email, created_at) VALUES (?, ?, ?, ?)",
        (session_id, name, email, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    return redirect(url_for("thank_you", name=name))


@app.route("/thank-you")
def thank_you():
    name = request.args.get("name", "")
    return render_template("thank_you.html", name=name)


def main():
    """Entry point for `ros2 run api_gateway web_form`."""
    init_db()
    # host="0.0.0.0" so it's reachable if the browser/kiosk runs on
    # a different device/screen than the Flask process (e.g. RVM controller)
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()
