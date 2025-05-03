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

for skill in skill_list:
    pattern = [{"LOWER": token} for token in skill.split()]
    matcher.add(skill, [pattern])


@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']
    if not file:
        return "no file uploaded."
    
    filename = file.filename

    if filename.endswith('.txt'):
        text = file.read().decode('utf-8')
    elif filename.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract.text() + '\n'
        if not text.strip():
            return "Could not extract text from PDF. Try another file."
    else:
        return "Please upload a .txt or .pdf file."

    doc = nlp(text)

    matches = matcher(doc)
    found_skills = set()

    for match_id, start, end in matches:
        span = doc[start:end]
        found_skills.add(span.text.lower())

    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return f"""
    <h3>Extracted Entities:</h3><pre>{entities}</pre>
    <h3>Detected Skills:</h3><pre>{list(found_skills)}</pre>
    """

if __name__ == '__main__':
    app.run(debug=True)