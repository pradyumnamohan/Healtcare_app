import google.generativeai as genai

genai.configure(api_key="AIzaSyDD6Snf1FKw-ovCFmcnEVnylntDpKgR5Ns")
model = genai.model("gemini-1.5-flash")
prompt = """Tell me somethings about google"""
respone = model