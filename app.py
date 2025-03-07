from flask import Flask, render_template, request, jsonify, url_for
from login import login_bp
from signup import signup_bp
import google.generativeai as genai
import os
import json
import time

app = Flask(__name__)
app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)

# Constant
FILE_PATH = "medical_conversations.json"
PERMANENT_PROMPT = """You are a first aid provider and not a doctor. you need to just advise the patient on what to do in the moment. It is known that the person will consult a doctor anyway but dont mention it explicitly. However if its serious, mention to meet the doctor as soon as possible. The conversation should be human like. Dont make it sound like the person is talking to a robot. Also do not deviate from the topic."""
GEMINI_API_KEY = "AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns"  # Replace with your actual API key

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def save_chat(query, response, summary=""):
    """Save chat to JSON file with query, response, and summary fields."""
    try:
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r") as file:
                data = json.load(file)
        else:
            data = []
        
        data.append({"query": query, "response": response, "summary": summary})
        
        with open(FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving chat: {e}")

def process_medical_query(user_query, model, medical_context=""):
    """Process user query and generate response with summary."""
    prompt = f"""{PERMANENT_PROMPT}

Current Query: {user_query}

Medical Context (for reference if needed): {medical_context}

Please provide a helpful first aid response:"""
    
    try:
        response = model.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            filtered_response = response.text.strip()
            return filtered_response
    except Exception as e:
        print(f"Error processing query: {e}")
    
    return "I'm sorry, I couldn't generate a response at the moment."

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/process_query', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'response': 'Please enter a valid query.'})
    
    response = process_medical_query(query, model)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
