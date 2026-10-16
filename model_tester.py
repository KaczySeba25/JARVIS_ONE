import os
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

# Ładowanie kluczy z .env
load_dotenv()

def test_groq():
    print("Testing Groq...", end=" ")
    try:
        client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": "Test: 1+1="}],
            max_tokens=10
        )
        print(f"✅ SUCCESS: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def test_nvidia():
    print("Testing NVIDIA...", end=" ")
    try:
        client = OpenAI(api_key=os.getenv("NVIDIA_API_KEY"), base_url="https://integrate.api.nvidia.com/v1")
        response = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[{"role": "user", "content": "Test: 1+1="}],
            max_tokens=10
        )
        print(f"✅ SUCCESS: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def test_gemini():
    print("Testing Google Gemini...", end=" ")
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Test: 1+1=")
        print(f"✅ SUCCESS: {response.text}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

def list_gemini_models():
    print("\n--- Available Gemini Models ---")
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Could not list models: {e}")

if __name__ == "__main__":
    print("=== JARVIS ONE: MULTI-MODEL DIAGNOSTICS ===\n")
    test_groq()
    test_nvidia()
    test_gemini()
    list_gemini_models()
    print("\n===========================================")
