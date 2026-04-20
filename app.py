
import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from utils.parser import extract_text
from utils.scorer import calculate_score

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

app = Flask(__name__)

# Upload folder setup
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file types
ALLOWED_EXTENSIONS = {"pdf", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# MAIN ROUTE (FAST)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        role = request.form["role"]
        file = request.files["resume"]

        # Validate file
        if file.filename == "" or not allowed_file(file.filename):
            return "Invalid or no file selected"

        # Ensure uploads folder exists
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Extract text
        resume_text = extract_text(filepath)

        # Calculate score
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


# AI ROUTE (OPTIONAL / SLOW)
@app.route("/ai-feedback", methods=["POST"])
def ai_feedback():
    role = request.form["role"]
    file = request.files["resume"]

    # Validate file
    if file.filename == "" or not allowed_file(file.filename):
        return "Invalid or no file selected"

    # Ensure uploads folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Save file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Extract text
    resume_text = extract_text(filepath)

    # Calculate score
    score, matched, required = calculate_score(resume_text, role)
    missing = list(set(required) - set(matched))

    # AI Suggestions
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful resume expert."},
                {"role": "user", "content": f"""
Role: {role}
Missing skills: {missing}

Resume:
{resume_text[:1000]}

Give short suggestions to improve the resume.
"""}
            ],
            timeout=20
        )

        feedback = response.choices[0].message.content

    except Exception as e:
        print(e)
        feedback = "AI service temporarily unavailable. Please try again later."

    return render_template(
        "index.html",
        score=score,
        matched=matched,
        missing=missing,
        feedback=feedback,
        role=role
    )


# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
