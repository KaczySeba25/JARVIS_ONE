"""Web research skill: fetch pages and return condensed text snippets.
"""
from tools import fetch_webpage


def run(arg=""):
    """arg can be a query or comma-separated URLs"""
    if not arg:
        return "Brak zapytania"
    parts = [p.strip() for p in arg.split(',') if p.strip()]
    out = []
    for p in parts:
        if p.startswith('http'):
            txt = fetch_webpage(p)
            out.append(f"URL: {p}\n{txt[:200]}...")
        else:
            # use simple search engine via duckduckgo html (lightweight)
            try:
                import requests
                q = p.replace(' ', '+')
                url = f'https://html.duckduckgo.com/html/?q={q}'
                r = requests.post(url, data={'q': p}, timeout=15)
                text = r.text
                out.append(f"Search results for: {p}\n{text[:200]}...")
            except Exception as e:
                out.append(f"Search error: {e}")
    return "\n\n".join(out)
