import os
import requests
from bs4 import BeautifulSoup
import skills_loader

def list_files(path="."):
    """Zwraca listę plików w katalogu roboczym."""
    try:
        files = os.listdir(path)
        return "\n".join(files) if files else "Katalog jest pusty."
    except Exception as e:
        return f"Błąd podczas odczytu katalogu: {e}"

def read_file(filepath):
    """Odczytuje zawartość wskazanego pliku."""
    try:
        if not os.path.exists(filepath):
            return f"Błąd: Plik '{filepath}' nie istnieje."
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Błąd podczas odczytu pliku: {e}"

def write_file(filepath, content):
    """Zapisuje treść do pliku (tworzy nowy lub nadpisuje)."""
    try:
        dirname = os.path.dirname(filepath)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Sukces: Zapisano plik '{filepath}'."
    except Exception as e:
        return f"Błąd podczas zapisu pliku: {e}"

def fetch_webpage(url):
    """Pobiera tekst strony internetowej."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)[:3000]
    except Exception as e:
        return f"Błąd podczas pobierania strony: {e}"

def run_skill(skill_name):
    """Wykonuje skill używając skills_loader.py."""
    try:
        result = skills_loader.execute_skill(skill_name)
        return f"Sukces wykonania skilla '{skill_name}':\n{result}"
    except Exception as e:
        return f"Błąd podczas wykonywania skilla '{skill_name}': {e}"
