import speech_recognition as sr
import argparse
import time
import sys
import os
from datetime import datetime
import google.generativeai as genai

genai.configure(api_key="AIzaSyDgHl1rjfupJKp93QXuSMgMTW3aggvsYqw")
model = genai.GenerativeModel("gemini-1.5-flash")

# Ensure proper encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Enhanced language options with more detailed information
LANGUAGE_OPTIONS = {
    "1": {
        "code": "kn-IN", 
        "name": "Kannada", 
        "native": "ಕನ್ನಡ",
        "greeting": "ನಮಸ್ಕಾರ",
        "speak_prompt": "ಈಗ ಮಾತನಾಡಿ...",
        "processing": "ನಿಮ್ಮ ಮಾತನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲಾಗುತ್ತಿದೆ..."
    },
    "2": {
        "code": "hi-IN", 
        "name": "Hindi", 
        "native": "हिन्दी",
        "greeting": "नमस्ते",
        "speak_prompt": "अब बोलिए...",
        "processing": "आपकी आवाज़ को प्रोसेस किया जा रहा है..."
    },
    "3": {
        "code": "en-IN", 
        "name": "English (Indian)", 
        "native": "English",
        "greeting": "Hello",
        "speak_prompt": "Please speak now...",
        "processing": "Processing your speech..."
    },
    "4": {
        "code": "ta-IN", 
        "name": "Tamil", 
        "native": "தமிழ்",
        "greeting": "வணக்கம்",
        "speak_prompt": "இப்போது பேசவும்...",
        "processing": "உங்கள் பேச்சு செயலாக்கப்படுகிறது..."
    },
    "5": {
        "code": "te-IN", 
        "name": "Telugu", 
        "native": "తెలుగు",
        "greeting": "నమస్కారం",
        "speak_prompt": "ఇప్పుడు మాట్లాడండి...",
        "processing": "మీ ప్రసంగం ప్రాసెస్ చేయబడుతోంది..."
    }
}

def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header(text):
    """Display formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")

def select_language():
    """
    Display enhanced language selection menu and return the selected language code
    
    Returns:
        dict: Selected language information
    """
    clear_screen()
    display_header("MULTILINGUAL VOICE TO TEXT CONVERTER")
    
    print("Available Languages:\n")
    
    for key, lang in LANGUAGE_OPTIONS.items():
        print(f"{key}. {lang['name']} ({lang['native']}) - {lang['greeting']}!")
    
    print("\nEnter your choice (1-5):")
    
    while True:
        choice = input("> ").strip()
        if choice in LANGUAGE_OPTIONS:
            selected = LANGUAGE_OPTIONS[choice]
            clear_screen()
            display_header(f"VOICE TO TEXT: {selected['name'].upper()}")
            print(f"{selected['greeting']}! You've selected {selected['name']} ({selected['native']})")
            return selected
        else:
            print("Invalid choice. Please enter a number between 1 and 5:")

def improve_recognition_settings(recognizer, language_code):
    """Apply language-specific recognition settings"""
    # Customize recognition parameters based on language
    if language_code.startswith("kn"):  # Kannada
        recognizer.energy_threshold = 4000  # Higher threshold for Kannada
        recognizer.dynamic_energy_threshold = True
        return 3  # Longer noise adjustment for Kannada
    elif language_code.startswith("hi"):  # Hindi
        recognizer.energy_threshold = 3500
        recognizer.dynamic_energy_threshold = True
        return 2.5
    elif language_code.startswith("ta") or language_code.startswith("te"):  # Tamil or Telugu
        recognizer.energy_threshold = 3800
        recognizer.dynamic_energy_threshold = True
        return 3
    else:  # English or others
        recognizer.energy_threshold = 3000
        recognizer.dynamic_energy_threshold = True
        return 2

def recognize_speech(language_info):
    """
    Records audio from the microphone and converts it to text in the selected language
    with enhanced language-specific settings.
    
    Args:
        language_info (dict): Dictionary containing language code and display info
    
    Returns:
        str: The recognized text in the original language or error message
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print(f"\n{language_info['greeting']}! {language_info['name']} ({language_info['native']}) mode activated.")
            
            # Apply language-specific recognition settings
            noise_duration = improve_recognition_settings(recognizer, language_info['code'])
            
            print(f"Adjusting for ambient noise. Please remain silent for {noise_duration} seconds...")
            recognizer.adjust_for_ambient_noise(source, duration=noise_duration)
            
            # Display prompts in both native language and English
            print(f"\n{language_info['speak_prompt']} (Speak now...)")
            
            # Use longer timeout for languages that might need more processing time
            timeout = 8 if language_info['code'].startswith(('kn', 'ta', 'te')) else 6
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=30)
            
            print(f"\n{language_info['processing']}")
            
            try:
                text = recognizer.recognize_google(audio, language=language_info['code'])
                return text
            except sr.UnknownValueError:
                return f"Speech not recognized. Please try speaking clearly in {language_info['name']}."
            except sr.RequestError as e:
                return f"Could not connect to Google Speech Recognition service; {e}"
    except Exception as e:
        return f"Error occurred: {e}"

def save_text(text, language_info):
    """
    Save recognized text to a file with proper encoding and timestamp
    
    Args:
        text (str): Text to save
        language_info (dict): Language information
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{language_info['name'].lower()}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Language: {language_info['name']} ({language_info['native']})\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(text)
    
    print(f"\nText saved to {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description="Enhanced Multilingual Voice to Text Converter")
    parser.add_argument("--continuous", action="store_true",
                        help="Enable continuous listening mode")
    parser.add_argument("--save", action="store_true",
                        help="Save recognized text to file")
    parser.add_argument("--lang", type=str, choices=["1", "2", "3", "4", "5"],
                        help="Directly select language (1=Kannada, 2=Hindi, 3=English, 4=Tamil, 5=Telugu)")
    
    args = parser.parse_args()
    
    # Handle language selection
    if args.lang and args.lang in LANGUAGE_OPTIONS:
        language_info = LANGUAGE_OPTIONS[args.lang]
        clear_screen()
        display_header(f"VOICE TO TEXT: {language_info['name'].upper()}")
        print(f"{language_info['greeting']}! Using {language_info['name']} ({language_info['native']})")
    else:
        language_info = select_language()
    
    if args.continuous:
        try:
            text_results = []
            session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            display_header(f"CONTINUOUS {language_info['name'].upper()} RECOGNITION MODE")
            print("Press Ctrl+C to stop recording and save results")
            
            while True:
                result = recognize_speech(language_info)
                
                # Display results with timestamps
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{timestamp}] {result}")
                
                # Store with timestamp
                text_results.append(f"[{timestamp}] {result}")
                
                time.sleep(1.5)  # Pause between recognition attempts
                
        except KeyboardInterrupt:
            print("\nStopping continuous recognition...")
            
            if args.save and text_results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{language_info['name'].lower()}transcript{timestamp}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Language: {language_info['name']} ({language_info['native']})\n")
                    f.write(f"Session: {session_start} to {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for item in text_results:
                        f.write(f"{item}\n")
                
                print(f"Complete transcript saved to {filename}")
    else:
        result = recognize_speech(language_info)
        
        # Format the display for better readability
        print("\n" + "-" * 60)
        print(f"RECOGNIZED {language_info['name'].upper()} TEXT:")
        print("-" * 60)
        print(f"{result}")
        print("-" * 60)
        prompt = f"""{result}.The result should be in the query language.{language_info}"""
        print(model.generate_content(prompt).text)

        
        if args.save:
            filename = save_text(result, language_info)
            print(f"Text has been saved to: {filename}")

if __name__ == "__main__":
    main()