import json
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key="AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns")
model = genai.GenerativeModel("gemini-1.5-flash")

FILE_PATH = "chat_history.json"
permanent="""You are a first aid provider and not a doctor. you need to just advise the patient on what to do in the moment. It is known that the person will consult a doctor anyway.However if its serious, mention to meet the doctor as soon as possible. The conversation should be human like. Dont make it sound like the person is talking to a robot.Also do not deviate from the topic."""

# Function to save chat to JSON (without printing)
def save_chat(query, response):
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
    else:
        data = []

    data.append({"query": query, "response": response})

    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

# Function to retrieve and print all stored chats
def get_chat_history():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
            print("Summary \n")
            for entry in data:
                summary = model.generate_content(f"Query: {entry['query']}\nResponse: {entry['response']}\n .Give me a summary of all these conversations.").text
                filtered_summary = "\n".join(summary.split("\n")[1:]).strip()
                print(filtered_summary)
    else:
        print("No chat history found.")

# Example query to Gemini
prompt = f"{permanent} I have a throat ache.Will it help?. What should I do?"
response = model.generate_content(prompt).text

# Remove first line (if needed)
filtered_response = "\n".join(response.split("\n")[1:]).strip()
print(filtered_response)

# Save to JSON file
save_chat(prompt, filtered_response)

# Retrieve and print stored records
get_chat_history()
