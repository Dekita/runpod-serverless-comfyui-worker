# import os
import json
import requests
import subprocess

# Load JSON data from the file
json_file_path = 'custom-files.json'  # Replace with the path to your JSON file
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# Iterate over each object in the JSON array
for item in data:
    url = item.get('url')
    path = item.get('path')

    if url and path:
        if url.endswith('.git'):
            try:# Clone the Git repository into the specified path
                subprocess.check_call(['git', 'clone', url, path])
                print(f"Cloned Git repository from {url} to {path}")
            except subprocess.CalledProcessError as e:
                print(f"Error cloning Git repository from {url}: {e}")
        else: 
            try:# Download model into the specified path
                response = requests.get(url)
                response.raise_for_status()
                with open(path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded {url} and saved it to {path}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")

print("Download process completed.")