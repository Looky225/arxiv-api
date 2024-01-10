import requests

# Replace with your FastAPI server URL and port
url = 'http://127.0.0.1:8000/process-query/'

# Replace with the desired arXiv paper ID and your question
data = {
    "paper_id": "2308.08155",
    "question": "What makes Autogen different ?"
}

# Send POST request
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    print("Query processed successfully.")
    print(response.json())  # Print the response content
else:
    print(f"Failed to process query: {response.status_code}, {response.text}")
