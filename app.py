from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")  # use a real secret in prod

# Basic Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/blog/<slug>")
def post(slug):
    return render_template("post.html", slug=slug)


if __name__ == "__main__":
    app.run(debug=True)
