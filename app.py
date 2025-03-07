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
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': filename
        })
    
    return jsonify({'success': False, 'message': 'Only PDF and JPEG files are allowed'})

@app.route('/')
def index():
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Emergency Healthcare</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manuale:wght@700&display=swap');
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #d5ecfc;
                text-align: center;
            }}
            .navbar {{
                background-color: #002147;
                padding: 15px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                position: relative;
                z-index: 1002;
            }}
            .left-section {{
                display: flex;
                align-items: center;
            }}
            .logo {{
                width: 40px;
                height: 40px;
                background-color: yellow;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-left: 10px;
            }}
            .emergency-btn {{
                background-color: yellow;
                border: none;
                padding: 10px 20px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 20px;
                cursor: pointer;
                margin-left: 20px;
            }}
            .dots-icon {{
                width: 30px;
                height: 30px;
                cursor: pointer;
                color: white;
                margin-right: 10px;
                position: relative;
                z-index: 1002;
            }}
            .container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 80vh;
            }}
            .title {{
                font-size: 32px;
                font-weight: bold;
                font-family: 'Manuale', serif;
                margin-bottom: 20px;
            }}
            .input-box {{
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: white;
                padding: 10px;
                border-radius: 20px;
                width: 60%;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}
            .input-box input {{
                border: none;
                outline: none;
                flex-grow: 1;
                padding: 10px;
                font-size: 16px;
                border-radius: 20px;
            }}
            .mic-icon {{
                width: 24px;
                height: 24px;
                cursor: pointer;
            }}
            .overlay {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
            }}
            .emergency-menu {{
                display: none;
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
                text-align: left;
                width: 300px;
                z-index: 1001;
                animation: fadeIn 0.3s ease-in-out;
            }}
            .more-menu {{
                display: none;
                position: fixed;
                top: 0;
                right: 0;
                width: 500px;
                height: 100%;
                background: white;
                box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
                z-index: 1001;
                animation: slideIn 0.3s ease-in-out;
                padding-top: 80px;
            }}
            .more-menu button {{
                display: block;
                width: 100%;
                padding: 20px 25px;
                border: none;
                background: none;
                font-size: 18px;
                text-align: left;
                cursor: pointer;
                transition: background-color 0.3s;
                color: #002147;
            }}
            .more-menu button:hover {{
                background-color: #f0f0f0;
            }}
            .response-container {{
                margin-top: 20px;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                width: 60%;
                text-align: left;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                display: none;
                max-height: 300px;
                overflow-y: auto;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}
            @keyframes slideIn {{
                from {{ transform: translateX(100%); }}
                to {{ transform: translateX(0); }}
            }}
        </style>
    </head>
    <body>
        <div class="navbar">
            <div class="left-section">
                <div class="logo">L</div>
                <button class="emergency-btn">Emergency</button>
            </div>
            <img src="{url_for('static', filename='more.png')}" class="dots-icon" alt="Menu">
        </div>
        <div class="container">
            <div class="title">Healthcare App</div>
            <div class="input-box">
                <input type="text" id="symptomInput" placeholder="Enter your symptoms" />
                <img src="https://cdn-icons-png.flaticon.com/512/709/709682.png" class="mic-icon" alt="Mic">
            </div>
            <div class="response-container" id="responseContainer">
                <div id="responseText"></div>
            </div>
        </div>
        
        <div class="overlay" id="overlay"></div>
        <div class="emergency-menu" id="emergencyMenu">
            <h2>Emergency Services</h2>
            <p><span>Press 1</span> for Ambulance 🚑🚑</p>
            <p><span>Press 2</span> for Fire Department 🚒🚒</p>
            <p><span>Press 3</span> for Police 🚓🚓</p>
        </div>
        
        <div class="more-menu" id="moreMenu">
            <button onclick="window.location.href='/'">Main Menu</button>
            <button onclick="window.location.href='/login'">Log In</button>
            <button onclick="window.location.href='/signup'">Sign Up</button>
        </div>

        <script>
            document.querySelector('.dots-icon').addEventListener('click', function() {{
                const moreMenu = document.getElementById('moreMenu');
                const overlay = document.getElementById('overlay');
                if (moreMenu.style.display === 'block') {{
                    moreMenu.style.display = 'none';
                    overlay.style.display = 'none';
                }} else {{
                    moreMenu.style.display = 'block';
                    overlay.style.display = 'block';
                }}
            }});

            document.getElementById('overlay').addEventListener('click', function() {{
                const moreMenu = document.getElementById('moreMenu');
                const emergencyMenu = document.getElementById('emergencyMenu');
                moreMenu.style.display = 'none';
                emergencyMenu.style.display = 'none';
                this.style.display = 'none';
            }});

            document.querySelector('.emergency-btn').addEventListener('click', function() {{
                const emergencyMenu = document.getElementById('emergencyMenu');
                const overlay = document.getElementById('overlay');
                emergencyMenu.style.display = 'block';
                overlay.style.display = 'block';
            }});

            document.addEventListener("keydown", function(event) {{
                const emergencyMenu = document.getElementById("emergencyMenu");
                const overlay = document.getElementById("overlay");
                const moreMenu = document.getElementById("moreMenu");
                
                if (event.key === "Escape") {{
                    if (emergencyMenu.style.display === "block") {{
                        emergencyMenu.style.display = "none";
                        overlay.style.display = "none";
                    }} else if (moreMenu.style.display === "block") {{
                        moreMenu.style.display = "none";
                        overlay.style.display = "none";
                    }} else {{
                        emergencyMenu.style.display = "block";
                        overlay.style.display = "block";
                    }}
                }} else if (emergencyMenu.style.display === "block") {{
                    if (event.key === "1") {{
                        alert("Calling Ambulance...🚑🚑");
                        window.location.href = "/emergency/ambulance";
                    }} else if (event.key === "2") {{
                        alert("Calling Fire Department...🚒🚒");
                        window.location.href = "/emergency/fire";
                    }} else if (event.key === "3") {{
                        alert("Calling Police...🚓🚓");
                        window.location.href = "/emergency/police";
                    }}
                }}
            }});

            // Process symptom input when user presses Enter
            document.getElementById('symptomInput').addEventListener('keydown', function(event) {{
                if (event.key === 'Enter') {{
                    const query = this.value.trim();
                    if (query) {{
                        processQuery(query);
                    }}
                }}
            }});

            // Function to process the query
            function processQuery(query) {{
                // Show loading state
                const responseContainer = document.getElementById('responseContainer');
                const responseText = document.getElementById('responseText');
                responseContainer.style.display = 'block';
                responseText.textContent = 'Processing your query...';

                // Send the query to the server
                fetch('/process_query', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ query: query }})
                }})
                .then(response => response.json())
                .then(data => {{
                    responseText.textContent = data.response;
                }})
                .catch(error => {{
                    responseText.textContent = 'Error processing your query. Please try again.';
                    console.error('Error:', error);
                }});
            }}
        </script>
    </body>
    </html>
    '''

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

if __name__ == '__main__':
    app.run(debug=True)