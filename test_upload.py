#!/usr/bin/env python3
"""
Test script for the Arabic STT API upload endpoint
"""
import requests
import json

def test_upload_endpoint():
    """Test the upload and process endpoint"""
    url = "http://localhost:8000/v1/upload-and-process"
    
    # Test with the test audio file
    try:
        with open("test_audio.wav", "rb") as audio_file:
            files = {"file": audio_file}
            data = {"language": "ar"}
            
            print("🧪 Testing upload endpoint...")
            print(f"📡 URL: {url}")
            print(f"📁 File: test_audio.wav")
            print(f"🌐 Language: Arabic")
            
            response = requests.post(url, files=files, data=data)
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
    except FileNotFoundError:
        print("❌ test_audio.wav not found")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_endpoint():
    """Test the health endpoint"""
    url = "http://localhost:8000/health"
    
    try:
        print("🏥 Testing health endpoint...")
        response = requests.get(url)
        
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_root_endpoint():
    """Test the root endpoint"""
    url = "http://localhost:8000/"
    
    try:
        print("🏠 Testing root endpoint...")
        response = requests.get(url)
        
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Root endpoint working:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Root endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    print("=" * 50)
    
    test_health_endpoint()
    print("\n" + "=" * 50)
    
    test_root_endpoint()
    print("\n" + "=" * 50)
    
    test_upload_endpoint()
    print("\n" + "=" * 50)
    print("✅ Tests completed!")