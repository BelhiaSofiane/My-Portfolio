from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")  # use a real secret in prod


from flask import request, session

@app.route('/set-theme', methods=['POST'])
def set_theme():
    data = request.get_json()
    session['theme'] = data.get('theme', 'light')
    return '', 204

@app.context_processor
def inject_theme():
    return {'theme': session.get('theme', 'light')}

# Basic Routes
@app.route("/")
def index():
    theme = session.get('theme', 'light')
    return render_template("index.html", theme=theme)

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
