from flask import Flask, request, render_template
import spacy
from spacy.matcher import Matcher
import pdfplumber

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

def load_skills(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

skill_list = load_skills('skills.txt')

matcher = Matcher(nlp.vocab)

# Create the matcher patterns for the skills
for skill in skill_list:
    pattern = [{"LOWER": token} for token in skill.split()]
    matcher.add(skill, [pattern])

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']
    job_description = request.form['job_description']
    
    if not file:
        return "No file uploaded."
    
    filename = file.filename

    # Extract resume text based on file type
    if filename.endswith('.txt'):
        text = file.read().decode('utf-8')
    elif filename.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        if not text.strip():
            return "Could not extract text from PDF. Try another file."
    else:
        return "Please upload a .txt or .pdf file."
    
    # Process resume text
    doc_resume = nlp(text)
    matches_resume = matcher(doc_resume)
    found_skills_resume = set()

    for match_id, start, end in matches_resume:
        span = doc_resume[start:end]
        found_skills_resume.add(span.text.lower())

    # Process job description text
    doc_job = nlp(job_description)
    matches_job = matcher(doc_job)
    found_skills_job = set()

    for match_id, start, end in matches_job:
        span = doc_job[start:end]
        found_skills_job.add(span.text.lower())

    # Calculate matching and missing skills
    matching_skills = found_skills_resume.intersection(found_skills_job)
    missing_skills = found_skills_job - found_skills_resume
    match_percentage = (len(matching_skills) / len(found_skills_job)) * 100 if found_skills_job else 0

    # Prepare output
    result = f"""
    <h3>Matching Skills:</h3><pre>{list(matching_skills)}</pre>
    <h3>Missing Skills from Resume:</h3><pre>{list(missing_skills)}</pre>
    <h3>Match Percentage: {match_percentage:.2f}%</h3>
    """

    return result


if __name__ == '__main__':
    app.run(debug=True)
