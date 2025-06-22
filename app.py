from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import requests
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")  # use a real secret in prod

@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    sofiane_context = """
    Sofiane Belhia is a web developer from Algeria.
    Education: Completed Harvard's CS50x and Scrimba Frontend Career Path.
    Skills: HTML, CSS (Tailwind CSS), JavaScript (React), Python (Flask), SQLite.
    Projects: Creator of this Personal Finance Monitoring application (CS50x Final Project), has a portfolio with other frontend apps.
    Work Style: Passionate, self-driven, focuses on clean code, modern UI/UX, user-centered design. Eager to learn new technologies.
    Goals: Actively seeking remote opportunities to contribute to real-world projects and collaborate.
    Contact: belhiasofiane150@gmail.com.
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant providing information about Sofiane Belhia, based on the provided context."},
        {"role": "user", "content": f"Here is context about Sofiane: {sofiane_context}\n\nUser's question: {user_query}"}
    ]

    # --- Read the API key from environment variables ---
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") # <--- MODIFIED LINE

    if not OPENROUTER_API_KEY:
        app.logger.error("OPENROUTER_API_KEY is not set in environment variables.")
        return jsonify({"response": "Server configuration error: API key missing."}), 500

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 150
            },
            timeout=30
        )
        response.raise_for_status()
        ai_response = response.json()
        
        ai_message_content = ai_response["choices"][0]["message"]["content"]
        return jsonify({"response": ai_message_content})

    except requests.exceptions.HTTPError as e:
        app.logger.error(f"HTTP Error from OpenRouter: {e.response.status_code} - {e.response.text}")
        return jsonify({"response": "Error reaching the AI service. Please try again later."}), 500
    except requests.exceptions.ConnectionError as e:
        app.logger.error(f"Connection Error to OpenRouter: {e}")
        return jsonify({"response": "Could not connect to the AI service. Check your internet connection."}), 500
    except requests.exceptions.Timeout as e:
        app.logger.error(f"Timeout Error from OpenRouter: {e}")
        return jsonify({"response": "The AI service took too long to respond. Please try again."}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return jsonify({"response": "An internal error occurred."}), 500

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
