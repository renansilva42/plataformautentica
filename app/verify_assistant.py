import os
import requests

def verify_assistant(assistant_id, api_key):
    base_url = "https://api.openai.com/v1"
    get_assistant_url = f"{base_url}/assistants/{assistant_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    try:
        response = requests.get(get_assistant_url, headers=headers, timeout=30)
        if response.status_code == 200:
            print(f"Assistant {assistant_id} found and accessible.")
            return True
        else:
            print(f"Assistant {assistant_id} not found or inaccessible. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error verifying assistant: {e}")
        return False

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("OPENAI_CAPIVARA_ANALISTA_ASSISTANT_ID")
    if not api_key or not assistant_id:
        print("Please set OPENAI_API_KEY and OPENAI_CAPIVARA_ANALISTA_ASSISTANT_ID environment variables.")
    else:
        verify_assistant(assistant_id, api_key)
