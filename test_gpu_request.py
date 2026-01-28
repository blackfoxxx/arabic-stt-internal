import requests
import os

# Use a file that exists or replace with one
file_path = r"c:\Users\pc\Documents\sst\arabic-stt-internal\public\uploads\54WP558N.mp3"
url = "http://localhost:8005/v1/upload-and-process"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    # Try to find any mp3 file in public/uploads
    upload_dir = r"c:\Users\pc\Documents\sst\arabic-stt-internal\public\uploads"
    if os.path.exists(upload_dir):
        files = [f for f in os.listdir(upload_dir) if f.endswith('.mp3')]
        if files:
            file_path = os.path.join(upload_dir, files[0])
            print(f"Using alternative file: {file_path}")
        else:
            print("No MP3 files found in uploads directory.")
            exit(1)
    else:
        print("Uploads directory not found.")
        exit(1)

print(f"Sending {file_path} to {url} with language='en'...")
with open(file_path, 'rb') as f:
    files = {'file': (os.path.basename(file_path), f, 'audio/mpeg')}
    data = {'language': 'en', 'model': 'large-v3'}
    try:
        response = requests.post(url, files=files, data=data, timeout=600)
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(response.json())
    except Exception as e:
        print(f"Request failed: {e}")
