import subprocess
import json
import time
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("BRIGHT_DATA_API_KEY")

def trigger_scraping_niche(api_key, keyword, num_of_posts, start_date, end_date, country, endpoint):

    payload = [{"keyword": keyword, 
                "num_of_posts": num_of_posts, 
                "start_date": start_date, 
                "end_date": end_date, 
                "country": country}]

    # Define the curl command
    command = [
        "curl",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),  # Convert payload to a JSON string
        endpoint
    ]

    # Execute the command and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Check if the command was successful
    if result.returncode == 0:
        try:
            # Parse the JSON response
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
            return None
    else:
        # Print the error if the command fails
        print(f"Error: {result.stderr}")
        return None

def trigger_scraping_channels(api_key, channel_urls, num_of_posts, start_date, end_date, order_by, country):
    
    dataset_id = "gd_lk56epmy2i5g7lzu0k"
    endpoint = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}&include_errors=true&type=discover_new&discover_by=url"

    payload = [
        {
            "url": url,
            "num_of_posts": num_of_posts,
            "start_date": start_date,
            "end_date": end_date,
            "order_by": order_by,
            "country": country
        }
        for url in channel_urls
    ]

    # Define the curl command
    command = [
        "curl",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),  # Convert payload to JSON string
        endpoint
    ]

    # Execute the command and capture the output
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        try:
            # Parse and return the JSON response
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
            return None
    else:
        # Print and return the error if the command fails
        print(f"Error: {result.stderr}")
        return None

def get_progress(api_key, snapshot_id):
    command = [
        "curl",
        "-H", f"Authorization: Bearer {api_key}",
        f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        return json.loads(result.stdout.strip())
    else:
        print(f"Error: {result.stderr}")
        return None

def get_output(api_key, snapshot_id, format="json"):

    # Define the curl command as a list
    command = [
        "curl",
        "-H", f"Authorization: Bearer {api_key}",
        f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format={format}"
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode == 0:
        json_lines = result.stdout.strip().split("\n")
        print(json_lines)
        json_objects = [json.loads(line) for line in json_lines]
        return json_objects
    else:
        print(f"Error: {result.stderr}")



