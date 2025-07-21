from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import requests
import sqlite3
import os

app = Flask(__name__)


# This function reads SVG files from the static directory and returns their content.
def load_svg(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
stack = [
    {"name": "HTML5", "svg": load_svg("static/svgs/html5.svg")},
    {"name": "CSS3", "svg": load_svg("static/svgs/css3.svg")},
    {"name": "JavaScript", "svg": load_svg("static/svgs/javascript.svg")},
    {"name": "React", "svg": load_svg("static/svgs/react.svg"), "spin": False}, 
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
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    sofiane_context = """
    Sofiane Belhia
    Age: 25
    Location: Algeria (Open to remote work)
    Email: belhiasofiane150@gmail.com
    GitHub: github.com/BelhiaSofianeCS50
    LinkedIn: linkedin.com/in/sofiane-belhia-1696b5285
    Portfolio: You are talking to ai from sofiane's portfolio.
    About Me:
    I'm a self-taught web developer with a strong foundation in frontend (HTML, CSS/Tailwind, JavaScript, React) and backend (Python, Flask, SQLite). I completed Harvard's CS50x and the Scrimba Frontend Career Path, and have built several responsive web applications focused on clean code, smooth UX, and modern design.
    Key Projects:
    Quizzical :  Quizzical is a trivia quiz app built with React. It fetches
        multiple-choice questions from the Open Trivia Database API and
        challenges users to test their knowledge in a fun and interactive way.
        Features include randomized answers, score tracking, and dynamic
        question loading — all wrapped in a responsive and minimalist design.
    tenzies : A fun, interactive game where you roll dice to get all the same number. Built with React.
    Budgeting-app: Budgeting App is a single-page application built with React and Vite that allows users to track their income and expenses. It features dynamic routing using React Router, and a simple UI for adding, viewing, and managing transactions. The app maintains state using React hooks and is designed for local use.
    Portfolio Website: A professional developer portfolio with theme toggle, and responsive design, everything you need to know about
    Other Frontend Projects: Include interactive components and responsive layouts built with React and Tailwind CSS.
    Work Ethic:
    Driven, detail-oriented, and constantly learning. I love building useful tools and working on meaningful problems. Currently looking for remote opportunities to grow, contribute, and collaborate in real-world environments.
    """

    messages = [
        {"role": "system", "content": "You are a helpful assistant providing information about Sofiane Belhia, based on the provided context. Do not deviate from this context. and do not answer any questions that are not related to Sofiane, if user doesnt ask anything about sofiane tell him that u are an assistant and please ask about sofiane"},
        {"role": "user", "content": f"Here is context about Sofiane: {sofiane_context}\n\nUser's question: {user_query}"}
    ]

    # --- Read the API key from environment variables ---
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") 

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
    return render_template("index.html", stack=stack)

@app.route("/projects")
def projects():
    return render_template("projects.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def blog():
    return render_template("about.html", stack=stack)



if __name__ == "__main__":
    app.run(debug=True)
