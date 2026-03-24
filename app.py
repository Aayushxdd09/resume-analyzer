import os
import requests
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from utils.parser import extract_text
from utils.scorer import calculate_score

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# 🟢 MAIN ROUTE (FAST)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        role = request.form["role"]
        file = request.files["resume"]

        # Ensure uploads folder exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        resume_text = extract_text(filepath)

        score, matched, required = calculate_score(resume_text, role)
        missing = list(set(required) - set(matched))

        return render_template(
            "index.html",
            score=score,
            matched=matched,
            missing=missing,
            role=role
        )

    return render_template("index.html")


# 🔵 AI ROUTE (SLOW BUT OPTIONAL)
@app.route("/ai-feedback", methods=["POST"])
def ai_feedback():
    role = request.form["role"]
    file = request.files["resume"]

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    resume_text = extract_text(filepath)

    score, matched, required = calculate_score(resume_text, role)
    missing = list(set(required) - set(matched))

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi",
                "prompt": f"""
                You are a resume expert.

                Role: {role}
                Missing skills: {missing}

                Resume:
                {resume_text[:1000]}

                Give short suggestions to improve the resume.
                """,
                "stream": False
            },
            timeout=40
        )

        feedback = response.json()["response"]

    except:
        feedback = "AI is slow or not responding. Try again."

    return render_template(
        "index.html",
        score=score,
        matched=matched,
        missing=missing,
        feedback=feedback,
        role=role
    )


if __name__ == "__main__":
    app.run(debug=True)