import secrets
from flask import Flask, render_template, request, jsonify, url_for
from login import login_bp
from signup import signup_bp
import google.generativeai as genai
from models import db, bcrypt  # Import from models
import os
import json
import time
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from PIL import Image
import pytesseract
import PyPDF2
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:BookClub123@localhost/HealthCareApp'
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns"  # Replace with your Gemini API key

# Constants
FILE_PATH = "medical_conversations.json"
PERMANENT_PROMPT = """You are a first aid provider and not a doctor. you need to just advise the patient on what to do in the moment. It is known that the person will consult a doctor anyway but dont mention it explicitly. However if its serious, mention to meet the doctor as soon as possible. The conversation should be human like. Dont make it sound like the person is talking to a robot. Also do not deviate from the topic."""

# Initialize extensions with app
db.init_app(app)
bcrypt.init_app(app)

# Initialize Gemini model
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"Error initializing Gemini API: {e}")
    model = None

# Import blueprints after initializing db and bcrypt
from login import login_bp
from signup import signup_bp
app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)

# Constants
FILE_PATH = "medical_conversations.json"
PERMANENT_PROMPT = """You are a first aid provider and not a doctor. you need to just advise the patient on what to do in the moment. It is known that the person will consult a doctor anyway but dont mention it explicitly. However if its serious, mention to meet the doctor as soon as possible. The conversation should be human like. Dont make it sound like the person is talking to a robot. Also do not deviate from the topic."""
GEMINI_API_KEY = "AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns"  # Replace with your Gemini API key

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_chat(query, response, summary=""):
    """Save chat to JSON file with query, response, and summary fields."""
    try:
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r") as file:
                data = json.load(file)
        else:
            data = []
        
        # Create entry with all three fields
        data.append({
            "query": query, 
            "response": response,
            "summary": summary
        })
        
        with open(FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving chat: {e}")

def summarize_content(text, model):
    """Generate a summary of the provided text using Gemini."""
    if not text or len(text) < 100:
        return "Text too short to summarize."
    
    try:
        summary_prompt = f"Summarize the following medical text concisely:\n\n{text[:4000]}"
        response = model.generate_content(summary_prompt)
        return response.text if hasattr(response, 'text') else "Unable to generate summary."
    except Exception as e:
        print(f"Error in summarization: {e}")
        return "Summary generation failed."

def process_medical_query(user_query, model, medical_context=""):
    """Process user query and generate response with summary."""
    # Construct prompt with medical context
    prompt = f"""{PERMANENT_PROMPT}

Current Query: {user_query}

Medical Context (for reference if needed): {medical_context}

Please provide a helpful first aid response:"""
    
    # Generate response
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            
            if hasattr(response, 'text') and response.text:
                filtered_response = response.text.strip()
                
                # Generate summary of the conversation
                conversation = f"Query: {user_query}\nResponse: {filtered_response}"
                summary = summarize_content(conversation, model)
                
                # Save to JSON with all fields
                save_chat(user_query, filtered_response, summary)
                
                return filtered_response, summary
            else:
                print(f"Empty response on attempt {attempt+1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        except Exception as e:
            print(f"Error on attempt {attempt+1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    # Fallback response
    fallback_response = "I'm sorry, I couldn't generate a response at the moment."
    fallback_summary = "Failed conversation about a medical issue."
    save_chat(user_query, fallback_response, fallback_summary)
    return fallback_response, fallback_summary

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            extracted_text = ""
            if filename.lower().endswith('.pdf'):
                with open(filepath, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
            else:
                image = Image.open(filepath)
                extracted_text = pytesseract.image_to_string(image)

            if not extracted_text.strip():
                return jsonify({
                    'success': False,
                    'message': 'No text could be extracted from the file'
                })

            summary = summarize_content(extracted_text, model)
            
            return jsonify({
                'success': True,
                'message': 'File processed successfully',
                'filename': filename,
                'summary': summary,
                'extracted_text': extracted_text[:1000]  # First 1000 chars for preview
            })

        except Exception as e:
            print(f"Error processing file: {e}")
            return jsonify({
                'success': False,
                'message': f'Error processing file: {str(e)}'
            })
    
    return jsonify({'success': False, 'message': 'Only PDF and JPEG files are allowed'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_query', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'response': 'Please enter a valid query.'})
    
    try:
        # Process the medical query and get the response
        response, summary = process_medical_query(query, model)
        return jsonify({'response': response, 'summary': summary})
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({'response': 'Sorry, I encountered an error processing your query.'})

@app.route('/emergency/<service>')
def emergency_redirect(service):
    return f"<h1>Redirecting to {service.capitalize()}...</h1>"

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    data = request.json
    spoken_text = data.get('spoken_text', '')
    
    if not spoken_text:
        return jsonify({'response': 'No speech detected.'})
    
    response = process_medical_query(spoken_text, model)
    return jsonify({'response': response})


if __name__ == '__main__':
    app.run(debug=True)