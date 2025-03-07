from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename
from login import login_bp
from signup import signup_bp
import google.generativeai as genai
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import json
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)

GEMINI_API_KEY = "AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to extract text from image

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {e}"

# Function to extract text from PDF

def extract_text_from_pdf(pdf_path):
    try:
        images = convert_from_path(pdf_path)
        text = "\n".join(pytesseract.image_to_string(img) for img in images)
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {e}"

# Route to display upload form
@app.route('/upload')
def upload_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Medical Document</title>
    </head>
    <body>
        <h2>Upload a Medical Document (PDF/JPG)</h2>
        <form action="/process_upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf,.jpg,.jpeg,.png" required>
            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    '''

# Route to process uploaded file
@app.route('/process_upload', methods=['POST'])
def process_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    if filename.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
    elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        extracted_text = extract_text_from_image(file_path)
    else:
        return jsonify({'error': 'Invalid file format'})
    
    if not extracted_text:
        return jsonify({'error': 'No text extracted from the document'})
    
    # Generate summary using Gemini API
    summary_prompt = f"Summarize this medical text in a few sentences:\n{extracted_text[:4000]}"
    response = model.generate_content(summary_prompt)
    summary = response.text.strip() if hasattr(response, 'text') else "Summary generation failed."
    
    return jsonify({'extracted_text': extracted_text, 'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
