# client.py
import requests
import json
import argparse
import time
# replace this URL with your exposed URL from the API builder. The URL looks like this
SERVER_URL = 'http://0.0.0.0:8000'

def main():
    parser = argparse.ArgumentParser(description="Send a query to the LitServe server.")
    parser.add_argument("--query", type=str, required=True, help="The query text to send to the server.")
    
    args = parser.parse_args()
    
    payload = {
        "query": args.query
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/predict", json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()['output']['raw']
        for token in result.split():
            print(token, end=" ", flush=True)
            time.sleep(0.05)

        # print(json.dumps(result, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    main()