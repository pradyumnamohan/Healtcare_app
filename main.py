#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
#AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns
import os
import json
import pdfplumber
import pytesseract
from PIL import Image
import google.generativeai as genai
import time

# Configure API
GEMINI_API_KEY = "AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns"  # Replace with your Gemini API key

# Constants
FILE_PATH = "medical_conversations.json"
PERMANENT_PROMPT = """You are a first aid provider and not a doctor. you need to just advise the patient on what to do in the moment. It is known that the person will consult a doctor anyway but dont mention it explicitly. However if its serious, mention to meet the doctor as soon as possible. The conversation should be human like. Dont make it sound like the person is talking to a robot. Also do not deviate from the topic."""

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

def main():
    """Main function to parse medical reports and handle queries."""
    # Configure Gemini API
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not set. Please update the script with your API key.")
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Error initializing Gemini API: {e}")
        return
        
    print("Medical Assistant System")
    print("=======================")
    
    # Ask for medical report paths
    report_files = []
    while True:
        report_path = input("\nEnter a medical report file path (PDF or image), or press enter to skip: ")
        if not report_path:
            break
        report_files.append(report_path)
    
    # Extract and process medical report context
    medical_context = ""
    if report_files:
        print("\nProcessing medical reports...")
        for file_path in report_files:
            if file_path.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                text = extract_text_from_image(file_path)
            else:
                print(f"Unsupported file format for {file_path}. Skipping.")
                continue
                
            if text and not text.startswith("Error"):
                medical_context += f"\nFrom {os.path.basename(file_path)}:\n{text}\n"
        
        # Summarize the medical context
        if medical_context:
            context_summary = summarize_content(medical_context, model)
            print(f"\nMedical reports summary: {context_summary}")
            medical_context = context_summary
    
    # Chat interface
    print("\n--- Chat Interface ---")
    while True:
        user_query = input("\nEnter your medical question (or type 'exit' to quit): ")
        if user_query.lower() in ['exit', 'quit', '']:
            break
        
        try:
            print("\nGenerating response...")
            response, summary = process_medical_query(user_query, model, medical_context)
            print(f"\nResponse: {response}")
            print(f"\nSummary: {summary}")
        except Exception as e:
            print(f"\nError processing query: {e}")

if __name__ == "__main__":
    main()