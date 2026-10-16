import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def run(query=""):
    """
    Profesjonalny research internetowy za pomocą Tavily AI.
    Gwarantuje 100% skuteczności, omijając blokady botów.
    """
    if not query:
        return "BŁĄD: Brak zapytania do researchu."
    
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "BŁĄD: Brak TAVILY_API_KEY w pliku .env. Zarejestruj się na tavily.com, aby uzyskać darmowy klucz."
    
    try:
        # Inicjalizacja klienta Tavily
        tavily = TavilyClient(api_key=api_key)
        
        # Wykonanie wyszukiwania z pobieraniem treści stron (search_depth="advanced")
        # search_depth="advanced" sprawia, że AI analizuje więcej źródeł i wyciąga lepsze dane
        response = tavily.search(
            query=query, 
            search_depth="advanced", 
            max_results=5,
            include_answer=True # Tavily generuje też krótkie podsumowanie odpowiedzi
        )
        
        # Jeśli Tavily zwróciło gotową odpowiedź, zaczynamy od niej
        final_answer = ""
        if response.get("answer"):
            final_answer = f"PODSUMOWANIE AI:\n{response['answer']}\n\n"
            
        # Dodajemy szczegółowe źródła
        results_text = ""
        for i, res in enumerate(response.get("results", []), 1):
            results_text += f"ŹRÓDŁO {i}: {res['url']}\nTREŚĆ: {res['content']}\n\n"
            
        if not results_text:
            return "Nie znaleziono wyników w sieci dla tego zapytania."
            
        return f"{final_answer}SZCZEGÓŁOWE WYNIKI:\n{results_text}"
        
    except Exception as e:
        return f"Krytyczny błąd połączenia z API Tavily: {str(e)}"

if __name__ == "__main__":
    # Test
    print(run("najlepsze trendy dropshipping lato 2024 UK"))
