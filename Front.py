from flask import Flask, render_template, request, jsonify, url_for, flash, session, redirect
import secrets
from models import db, bcrypt  # Import from models
import os
import json
import pdfplumber
import pytesseract
from PIL import Image
import google.generativeai as genai
import time

# Initialize the Flask app
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

# Register blueprints with consistent url_prefix
app.register_blueprint(login_bp, url_prefix='/auth')
app.register_blueprint(signup_bp, url_prefix='/auth')

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file using pdfplumber."""
    if not os.path.exists(pdf_path):
        return f"Error: PDF file not found at {pdf_path}"
    
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    if not os.path.exists(image_path):
        return f"Error: Image file not found at {image_path}"
    
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip() if text else "No text found in image."
    except Exception as e:
        return f"Error extracting text from image: {e}"

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
        summary_prompt = f"Summarize this text briefly in one paragraph:\n{text[:4000]}"
        response = model.generate_content(summary_prompt)
        
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            return "Unable to generate summary."
    except Exception as e:
        print(f"Error generating summary: {e}")
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def handle_query():
    """API endpoint to handle medical queries from the frontend"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Please log in to use the medical assistant'
        }), 401
    
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({
                'status': 'error',
                'message': 'Please enter your symptoms or question'
            }), 400
        
        # Initialize the model
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'Medical assistant is currently unavailable'
            }), 500
        
        # Process the query using the imported function
        response, summary = process_medical_query(user_query, model)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request'
        }), 500

@app.route('/emergency/<service>')
def emergency_redirect(service):
    return f"<h1>Redirecting to {service.capitalize()}...</h1>"

if __name__ == '__main__':
    app.run(debug=True)