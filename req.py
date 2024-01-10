import requests

# Replace with your FastAPI server URL and port
url = 'http://127.0.0.1:8000/download-arxiv/'

# Replace with the desired arXiv paper ID
data = {
    "paper_id": "2308.08155"
}

# Send POST request
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    print("Paper downloaded successfully.")
else:
    print(f"Failed to download paper: {response.status_code}, {response.text}")
