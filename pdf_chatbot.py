import os
import pdfplumber
import re
import nltk
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Ensure NLTK tokenizer is available
nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize

# Load T5 Model for QA
model_name = "google/flan-t5-large"
tokenizer = T5Tokenizer.from_pretrained(model_name ,Legacy=False)
model = T5ForConditionalGeneration.from_pretrained(model_name)

PROJECT_UPLOAD_FOLDER = "uploads"
EXTERNAL_UPLOAD_FOLDER = "C:/Saved_PDFs"

# Ensure both folders exist
os.makedirs(PROJECT_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTERNAL_UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extracts and cleans text from a given PDF file."""
    text = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    cleaned_text = re.sub(r'\s+', ' ', page_text.strip())
                    text.append(cleaned_text)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    return " ".join(text) if text else None

def generate_answer(question, context):
    """Generates the best possible answer using T5."""
    if not context:
        return "No text found in the PDF."
    input_text = f"question: {question} context: {context}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_length=150)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
