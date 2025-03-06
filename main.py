import requests

API_URL = "https://api-inference.huggingface.co/models/medicalai/ClinicalBERT"
HEADERS = {"Authorization": "Bearer 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"}  # Replace with your correct API key

def query_medicalbert(text):
    payload = {"inputs": text}
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    # Print raw response to debug
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text)  # This will help you see what the API is returning

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Invalid JSON response from API"}

# Example usage
medical_text = "I'm feeling sleepy, can I use adderall [MASK]?"

result = query_medicalbert(medical_text)
print(result)
