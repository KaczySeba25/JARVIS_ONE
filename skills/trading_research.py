"""Skill: trading_research

Szybki skill do zebrania i podsumowania kluczowych informacji o tradingu i AI agentach do tradingu.
Użyje skills/web_research oraz prostego HTTP search do zebrania fragmentów.
"""

from skills import web_research


def run(arg=""):
    """Arg can be a comma-separated list of queries or URLs.
    Example: "trading basics, algorithmic trading, backtesting frameworks, ccxt, testnet"
    """
    if not arg:
        return "Podaj zapytania. Przykład: trading basics, backtesting frameworks, ccxt"
    queries = [q.strip() for q in arg.split(',') if q.strip()]
    results = []
    for q in queries:
        try:
            # use web_research skill to fetch and condense
            res = web_research.run(q)
            results.append(f"---\nQuery: {q}\n{res[:2000]}\n")
        except Exception as e:
            results.append(f"---\nQuery: {q} -> error: {e}\n")
    summary = "\n".join(results)
    # save short note to semantic memory if available
    try:
        import semantic_memory as sm
        sm.save_memory('research', 'trading_research', summary[:1000])
    except Exception:
        pass
    return summary
