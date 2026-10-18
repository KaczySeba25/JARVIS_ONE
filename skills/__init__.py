"""Skill wyszukiwania internetowego z fallbackiem do DuckDuckGo.

- Najpierw używa Tavily, jeśli istnieje klucz TAVILY_API_KEY
- Następnie przechodzi do DuckDuckGo Search, jeśli brak klucza lub wystąpi błąd
- Zawsze zwraca odpowiedź tekstową, bez pętli i bez przerywania agenta
"""
import os
from typing import Any


def _run_duckduckgo(query: str, max_results: int = 5) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
        if not results:
            return "Nie znaleziono wyników w sieci dla podanego zapytania."

        chunks = []
        for idx, item in enumerate(results, start=1):
            title = item.get("title") or "Brak tytułu"
            href = item.get("href") or item.get("url") or ""
            body = item.get("body") or item.get("text") or ""
            chunks.append(f"ŹRÓDŁO {idx}: {title}\nURL: {href}\nOpis: {body}\n---")
        return "\n".join(chunks)
    except Exception as exc:
        return f"Błąd DuckDuckGo Search: {exc}. Zainstaluj zależności za pomocą python scripts/bootstrap_agent.py."


def run(query: str = "") -> str:
    if not query:
        return "BŁĄD: Brak zapytania do researchu."

    api_key = os.getenv("TAVILY_API_KEY")
    if api_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True,
            )

            answer = response.get("answer")
            results = response.get("results", [])
            if answer or results:
                text = []
                if answer:
                    text.append(f"PODSUMOWANIE AI:\n{answer}\n")
                for idx, res in enumerate(results, start=1):
                    url = res.get("url") or ""
                    content = res.get("content") or ""
                    text.append(f"ŹRÓDŁO {idx}: {url}\nTREŚĆ: {content}\n---")
                return "\n".join(text)
        except Exception:
            pass

    return _run_duckduckgo(query)


if __name__ == "__main__":
    print(run("Binance Testnet BTC/USDT price and volume analysis"))
