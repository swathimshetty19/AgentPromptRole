#!/usr/bin/env python3
"""
Quick test script to verify your Qwen API key works.
Run this from your project root with your venv activated.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_qwen_api_key():
    """Test if QWEN_API_KEY is valid and working."""
    
    print("=" * 60)
    print("QWEN API KEY TEST")
    print("=" * 60)
    
    # Check if key exists
    api_key = os.getenv("QWEN_API_KEY")
    
    if not api_key:
        print("❌ QWEN_API_KEY not found in environment!")
        print("\nMake sure you:")
        print("1. Added QWEN_API_KEY to your .env file")
        print("2. Restarted your terminal/script")
        print("3. Are in the correct directory")
        return False
    
    print(f"✅ QWEN_API_KEY found (length: {len(api_key)})")
    print(f"   Key starts with: {api_key[:10]}...")
    
    # Test API call
    print("\n📡 Testing API connection...")
    
    url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    body = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "user", "content": "Say 'Hello! API key is working!' if you can read this."}
        ]
    }
    
    try:
        response = requests.post(url, json=body, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            
            print("\n✅ SUCCESS! API key is valid and working!")
            print("\n📨 Response from Qwen:")
            print("-" * 60)
            print(message)
            print("-" * 60)
            print("\n🎉 Your Qwen API setup is complete and ready to use!")
            return True
            
        elif response.status_code == 401:
            print("\n❌ AUTHENTICATION FAILED!")
            print("   Error: Invalid API key")
            print("\nPossible issues:")
            print("  - API key is incorrect")
            print("  - API key is from Beijing region (use Singapore region)")
            print("  - API key was deleted or expired")
            print(f"\n  Response: {response.text}")
            return False
            
        elif response.status_code == 429:
            print("\n⚠️  RATE LIMIT EXCEEDED")
            print("   You've hit the API rate limit")
            print("   Wait a moment and try again")
            return False
            
        else:
            print(f"\n❌ API ERROR: Status code {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ REQUEST TIMEOUT")
        print("   The API request took too long")
        print("   Check your internet connection")
        return False
        
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR")
        print("   Could not connect to Qwen API")
        print("   Check your internet connection")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Qwen API Key Test\n")
    
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("❌ 'requests' library not found!")
        print("   Install it with: pip install requests")
        exit(1)
    
    # Check if dotenv is installed
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("⚠️  'python-dotenv' not found (optional)")
        print("   Install it with: pip install python-dotenv")
        print("   Or set QWEN_API_KEY as an environment variable\n")
    
    # Run the test
    success = test_qwen_api_key()
    
    if success:
        print("\n✅ All tests passed! You're ready to use Qwen models.")
    else:
        print("\n❌ Test failed. Please fix the issues above and try again.")
    
    print()
