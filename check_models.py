import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    
    print("Łączenie z Groq w celu pobrania listy dostępnych modeli...")
    models = client.models.list()
    
    print("\n--- DOSTĘPNE MODELE DLA TWOJEGO KLUCZA ---")
    for model in models.data:
        print(model.id)
    print("----------------------------------------")

except Exception as e:
    print(f"BŁĄD PODCZAS POBIERANIA LISTY: {str(e)}")
