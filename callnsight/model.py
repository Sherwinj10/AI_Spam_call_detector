import google.generativeai as genai
import json
import re

def gemini_model(message):
    genai.configure(api_key="paste_your_api_key")
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompts = [
        "give answer only in json format, label: 1 for spam or 0 for ham for the following and risk_factor: the probability that the given statement is spam",
        f"{message}",
    ]
    try:
        response = model.generate_content(prompts)
        # Extract JSON using regex
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            json_response = json.loads(json_str)
            
            label = json_response.get('label')
            risk = json_response.get('risk_factor')
            print(f"label: {label}\tRisk_factor: {risk}") 
            return label, risk
        else:
            print("No JSON found in response")
            return None, None
    
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None
