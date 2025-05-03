from flask import Flask, request, render_template
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

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
        with pdfplumber.opem(file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract.text() + '\n'
        if not text.strip():
            return "Could not extract text from PDF. Try another file."
    else:
        return "Please upload a .txt or .pdf file."

    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return f"<h3>Extracted Entities:</h3><pre>{entities}</pre>"

if __name__ == '__main__':
    app.run(debug=True)