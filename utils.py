from PyPDF2 import PdfReader
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content

    return text


# Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return text


# Rank resumes
def rank_resumes(job_desc, resumes):
    documents = [job_desc] + resumes

    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=1000
    )
    vectors = vectorizer.fit_transform(documents)

    scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    # Normalize scores (clean and mathematically valid)
    if scores.max() > 0:
        scores = scores / scores.max()

    return scores.tolist()


# Keyword matching (NEW FEATURE)
def get_matching_keywords(job_desc, resume):
    job_words = set(job_desc.split())
    resume_words = set(resume.split())
    return list(job_words.intersection(resume_words))

def interpret_score(score):
    if score > 0.5:
        return "Strong Match ✅"
    elif score > 0.25:
        return "Moderate Match ⚠️"
    else:
        return "Low Match ❌"