ROLE_SKILLS = {
    "Data Analyst": ["python", "sql", "excel", "pandas", "matplotlib"],
    "Backend Developer": ["python", "flask", "api", "database", "docker"],
    "AI Engineer": ["python", "machine learning", "nlp", "tensorflow", "pytorch"]
}

def calculate_score(resume_text, role):
    resume_text = resume_text.lower()
    required_skills = ROLE_SKILLS.get(role, [])

    matched_skills = []

    for skill in required_skills:
        if skill in resume_text:
            matched_skills.append(skill)

    score = 0
    if len(required_skills) > 0:
        score = int((len(matched_skills) / len(required_skills)) * 100)

    return score, matched_skills, required_skills