import requests

# Replace with your FastAPI server URL and port
url = 'http://127.0.0.1:8000/download-arxiv/'

# Replace with the desired arXiv paper ID
data = {
    "paper_id": "1605.08386v1"  # Example: "1605.08386v1"
}

# Send POST request
response = requests.post(url, json=data)

# Check if the request was successful
if response.status_code == 200:
    # Save the file
    with open('downloaded_paper.pdf', 'wb') as f:
        f.write(response.content)
    print("Paper downloaded successfully.")
else:
    print(f"Failed to download paper: {response.status_code}, {response.text}")
