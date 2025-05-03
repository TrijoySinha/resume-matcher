import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("John Smith is a software engineer skilled in Python and Django.")

for ent in doc.ents:
    print(ent.text, ent.label_)