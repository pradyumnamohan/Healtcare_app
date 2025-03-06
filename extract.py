import pdfplumber
import pytesseract
from PIL import Image
import requests

# Hugging Face API for Summarization
HF_API_KEY = "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"  # Replace with your Hugging Face API key
SUMMARIZATION_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using pdfplumbe and summarise the same."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def summarize_text(text):
    """Summarizes extracted text using a Hugging Face model."""
    payload = {"inputs": text}
    response = requests.post(SUMMARIZATION_API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        return f"Error: {response.json()}"


# Example Usage
pdf_text = extract_text_from_pdf("hosp2.pdf")
image_text = extract_text_from_image("hosp1.png")

# Combine texts if needed
full_text = pdf_text + "\n" + image_text
summary = summarize_text(full_text)

print("Extracted Text:\n", full_text)
print("\nSummarized Text:\n", summary)
