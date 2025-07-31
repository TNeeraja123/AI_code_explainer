from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from datetime import datetime
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

DB_PATH = 'code_snippets.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS snippets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL,
                        explanation TEXT,
                        timestamp TEXT
                    )''')
        conn.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, use_reloader=False)


# Enhanced explanation logic: line-by-line

def explain_code(code):
    lines = code.strip().splitlines()
    explanations = []

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        if not stripped:
            explanations.append({"line": line, "explanation": "This line is empty or contains only whitespace."})
        elif stripped.startswith("#"):
            explanations.append({"line": line, "explanation": "This is a comment line."})
        elif "import" in stripped:
            explanations.append({"line": line, "explanation": "This line imports a module or library."})
        elif stripped.startswith("def "):
            explanations.append({"line": line, "explanation": "This defines a function."})
        elif stripped.startswith("class "):
            explanations.append({"line": line, "explanation": "This defines a class."})
        elif "for " in stripped and " in " in stripped:
            explanations.append({"line": line, "explanation": "This is a loop iterating over an iterable."})
        elif "if " in stripped:
            explanations.append({"line": line, "explanation": "This is a conditional statement."})
        elif "elif " in stripped:
            explanations.append({"line": line, "explanation": "This is an else-if condition block."})
        elif "else" in stripped:
            explanations.append({"line": line, "explanation": "This is an else block for fallback logic."})
        elif "=" in stripped:
            explanations.append({"line": line, "explanation": "This line assigns a value to a variable."})
        else:
            explanations.append({"line": line, "explanation": "This line performs an operation or function call."})

    return explanations

@app.route('/api/explain', methods=['POST'])
def explain():
    data = request.get_json()
    code = data.get('code', '')

    if not code.strip():
        return jsonify({'error': 'Empty code'}), 400

    explanation_list = explain_code(code)
    timestamp = datetime.now().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO snippets (code, explanation, timestamp) VALUES (?, ?, ?)",
                  (code, str(explanation_list), timestamp))
        conn.commit()

    return jsonify({'explanations': explanation_list})

@app.route('/api/snippets', methods=['GET'])
def get_snippets():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT code, explanation, timestamp FROM snippets ORDER BY id DESC LIMIT 10")
        rows = c.fetchall()
        return jsonify([{ 'code': row[0], 'explanation': row[1], 'timestamp': row[2] } for row in rows])


from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Flask is working!'

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000)