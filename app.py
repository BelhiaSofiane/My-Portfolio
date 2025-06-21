import os
import requests
import sqlite3 
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Load environment variables from .env file at the very beginning
load_dotenv()

app = Flask(__name__)

# --- IMPORTANT: Configure SECRET_KEY for session security ---
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.urandom(24).hex()) # Fallback for dev, but should be in .env!

# --- Load SVG content from files (recommended for cleaner code) ---
def load_svg(filepath):
    """Loads SVG content from a given file path."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        app.logger.error(f"SVG file not found: {filepath}")
        return "" # Return empty string or a placeholder SVG

# Assuming SVGs are in a 'static/svgs' directory
stack = [
    {"name": "HTML5", "svg": load_svg("static/svgs/html5.svg")},
    {"name": "CSS3", "svg": load_svg("static/svgs/css3.svg")},
    {"name": "JavaScript", "svg": load_svg("static/svgs/javascript.svg")},
    {"name": "React", "svg": load_svg("static/svgs/react.svg"), "spin": True}, # Note: spin attribute handled by frontend
    {"name": "Python", "svg": load_svg("static/svgs/python.svg")},
    {"name": "Flask", "svg": load_svg("static/svgs/flask.svg")},
    {"name": "SQLite", "svg": load_svg("static/svgs/sqlite.svg")},
    {"name": "Git", "svg": load_svg("static/svgs/git.svg")},
    {"name": "Tailwind CSS", "svg": load_svg("static/svgs/tailwindcss.svg")},
    {"name": "Jinja2", "svg": load_svg("static/svgs/jinja2.svg")},
    {"name": "VS Code", "svg": load_svg("static/svgs/vscode.svg")},
    {"name": "Terminal / CLI", "svg": load_svg("static/svgs/terminal.svg")}
]


@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    """Handles AI chat requests, fetches response from OpenRouter."""
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Define Sofiane's context for the AI
    sofiane_context = """
    Sofiane Belhia is a web developer from Algeria, specializing in frontend development with a focus on modern web technologies, age 25 years old.
    2023: Started my coding journey — learned HTML, CSS, and JavaScript, from scrimba 
    2024: Finished Scrimba’s Frontend Career Path.
    2025: Finished CS50x harvard into to computer sciense Building real-world projects with Flask, React, and Tailwind. Looking for my first developer role.
    projects :
        tenzies: 
            live demo : https://smb-tenzies-game.netlify.app/
            github : https://github.com/KunoSMB/tenziesgame
        quizzical:
            live demo : https://smb-quizzical.netlify.app/
            github : https://github.com/KunoSMB/Quizzical-Revise
    Github : https://github.com/BelhiaSofianeCS50/
    Linkedin : https://www.linkedin.com/in/belhia-sofiane-150/
    Education: Completed Harvard's CS50x and Scrimba Frontend Career Path.
    Skills: HTML, CSS (Tailwind CSS), JavaScript (React), Python (Flask), SQLite.
    Projects: Creator of this Personal Finance Monitoring application (CS50x Final Project), has a portfolio with other frontend apps.
    Work Style: Passionate, self-driven, focuses on clean code, modern UI/UX, user-centered design. Eager to learn new technologies.
    Goals: Actively seeking remote opportunities to contribute to real-world projects and collaborate.
    Contact: belhiasofiane150@gmail.com.
    """

    messages = [
        {"role": "system", "content": "Queries will not add to your knowledge ,If you are asked anything that is not about Sofiane Belhia, do NOT answer. You are a professional and helpful assistant, providing information about Sofiane Belhia. All information must be derived solely from the context provided within the user's current prompt. Ensure your responses are concise and directly address the user's query without unnecessary detail."},
        {"role": "user", "content": f"Here is context about Sofiane: {sofiane_context}\n\nUser's question: {user_query}"}
    ]

    # Retrieve API key from environment variables
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    if not OPENROUTER_API_KEY:
        # Log a critical error if the key is missing
        app.logger.critical("OPENROUTER_API_KEY is not set in environment variables. AI functionality will not work.")
        return jsonify({"response": "Server configuration error: AI service API key is missing."}), 500

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto", # Or a specific model like "mistralai/mistral-7b-instruct:free"
                "messages": messages,
                "temperature": 0.7, # Controls randomness (0.0-1.0)
                "max_tokens": 150 # Limits the length of the AI's response
            },
            timeout=30 # Set a timeout for the API request
        )
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        ai_response = response.json()

        # Extract the content from the AI's response
        ai_message_content = ai_response["choices"][0]["message"]["content"]
        return jsonify({"response": ai_message_content})

    except requests.exceptions.HTTPError as e:
        app.logger.error(f"HTTP Error from OpenRouter ({e.response.status_code}): {e.response.text}")
        return jsonify({"response": "Error from AI service: " + e.response.text[:100] + "..."}), 500
    except requests.exceptions.ConnectionError as e:
        app.logger.error(f"Connection Error to OpenRouter: {e}")
        return jsonify({"response": "Could not connect to the AI service. Check internet connection."}), 500
    except requests.exceptions.Timeout as e:
        app.logger.error(f"Timeout Error from OpenRouter: {e}")
        return jsonify({"response": "The AI service took too long to respond. Please try again."}), 500
    except requests.exceptions.RequestException as e:
        # Catch any other requests-related errors
        app.logger.error(f"A general request error occurred with OpenRouter: {e}")
        return jsonify({"response": "An issue occurred while communicating with the AI service."}), 500
    except KeyError:
        # Handle cases where the expected keys are not in the AI response
        app.logger.error(f"Unexpected AI response format: {ai_response}")
        return jsonify({"response": "Received an unexpected response from the AI service."}), 500
    except Exception as e:
        # Catch any other unexpected errors
        app.logger.error(f"An unexpected error occurred in ask_ai: {e}")
        return jsonify({"response": "An internal server error occurred."}), 500


@app.route('/set-theme', methods=['POST'])
def set_theme():
    """Sets the user's preferred theme in the session."""
    data = request.get_json()
    session['theme'] = data.get('theme', 'light')
    return '', 204 # No content response

@app.context_processor
def inject_theme():
    """Injects the current theme into all templates."""
    return {'theme': session.get('theme', 'light')}

# Basic Routes
@app.route("/")
def index():
    """Renders the main index page."""
    theme = session.get('theme', 'light')
    return render_template("index.html", theme=theme, stack=stack)

@app.route("/projects")
def projects():
    """Renders the projects page."""
    return render_template("projects.html")

@app.route("/contact")
def contact():
    """Renders the contact page."""
    return render_template("contact.html")

@app.route("/about")
def about():
    """Renders the about page."""
    return render_template("about.html")


if __name__ == "__main__":
    # In production, use a WSGI server like Gunicorn or uWSGI
    # For development, debug=True is okay but never use in production
    app.run(debug=True)