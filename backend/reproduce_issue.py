import sys
import os

# Add the current directory to sys.path so we can import from backend
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_analyze():
    print("Testing /api/markets/analyze...")
    response = client.post(
        "/api/markets/analyze",
        json={"country_name": "France"}
    )
    
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print("Response Body:")
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            analysis = data.get("analysis", {})
            score = analysis.get("score")
            reasoning = analysis.get("reasoning")
            print(f"Score: {score}")
            print(f"Reasoning: {reasoning}")
            
            if score == 0 and reasoning == "Analysis failed.":
                print("FAILURE: Analysis failed (likely Gemini issue).")
            elif score is not None:
                print("SUCCESS: Analysis returned a score.")
            else:
                print("FAILURE: Analysis missing score.")
        else:
            print("FAILURE: API returned error status.")
            
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(response.text)

if __name__ == "__main__":
    test_analyze()
