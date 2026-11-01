"""Przykładowy skill: hello_world

Ten skill pokazuje jak napisać prosty plik w katalogu skills/.
Wymaga, aby w repo znajdował się moduł `semantic_memory` — wtedy skill może zapisywać i odczytywać pamięć.
"""

def run(arg=""):
    try:
        import semantic_memory as sm
    except Exception:
        sm = None

    text = "Cześć! Jestem przykładowym skillem HELLO_WORLD."
    if arg:
        text += f" Otrzymałem argument: {arg}" 

    if sm:
        sm.save_memory("skill","hello_world","Uruchomiono skill hello_world z arg: " + str(arg))
        text += "\n(Zapisałem krótką notatkę do pamięci.)"
    else:
        text += "\n(Brak modułu semantic_memory — nie zapisałem pamięci.)"

    return text
