Instrukcja zmian i dalsze kroki - feature/jarvis-improvements

Co dodałem w tym branchu:
- skills/hello_world.py  -> przykładowy skill, pokazuje zapis do pamięci
- semantic_memory.py     -> prosty, plikowy magazyn pamięci (data_vault/memory.json)
- vault_manager.py       -> prosty manager zapisujący "credentials" w data_vault/vault.json

Dlaczego to może pomóc:
- agent.py w repo próbuje importować `semantic_memory` oraz `vault_manager`. Gdy dodasz
  te pliki, agent będzie miał prostą, trwałą pamięć (persist); to podstawowy krok ku
  "uczeniu się" i zapamiętywaniu kontekstu pomiędzy uruchomieniami.
- Przykładowy skill pokazuje jak zapisać notatkę do pamięci i jak stworzyć prosty skill
  który można wywołać z [RUN_SKILL: hello_world].

Następne zalecane kroki (mogę zrobić je za Ciebie jeśli chcesz):
1) Udoskonalenie routera modeli:
   - Wprowadzić retry/backoff i priorytet listy providerów (GROQ, NVIDIA, HuggingFace, lokalne modele).
   - Dodać możliwość używania lokalnych, open-source modeli (gpt4all/llama.cpp) jako najtańszy fallback
     (wymaga instalacji dodatkowego oprogramowania i może być wolne na Codespaces).
   - Cache'ować odpowiedzi dłuższych konwersacji (np. w pliku lub bazie) by ograniczyć zapytania do API.

2) Pamięć wektorowa / semantyczna (opcjonalnie):
   - Zamiast prostego JSON, można dodać SQLite + prosty wektor store (np. użyć sentence-transformers lokalnie)
     lub integrację z bezpłatnym embedding providerem. To pozwoli na semantyczne wyszukiwanie pamięci.

3) Uczenie się i samonaprawa:
   - Dodać healthchecky i retry'y dla wywołań narzędzi, logowanie błędów i automatyczne próby naprawy
     (np. re-install brakujących bibliotek, restart procesu, zgłoszenie w historii pamięci).
   - Wprowadzić "human-in-loop" dla krytycznych kroków: w przypadku potrzeby weryfikacji (SMS, CAPTCHA)
     Jarvis powinien zapisać szczegóły do pamięci i poprosić Cię o interwencję — TA JAKTYKA JEST BEZPIECZNA
     i ZGODNA Z PRAWDZIWYMI REGUŁAMI.

Bezpieczeństwo i ważne granice (ważne - przeczytaj):
- Nie pomogę Ci tworzyć ani udostępniać kodu, który by omijał zabezpieczenia serwisów (CAPTCHA, SMS verification),
  ani automatyzował masowe tworzenie kont w sposób niezgodny z regulaminami. Nie dam instrukcji do obejścia
  zabezpieczeń.
- Bezpieczne alternatywy:
  - Korzystanie z oficjalnych API i partnerstw (jeśli dostępne).
  - Użycie usług SMS (np. Twilio) do legalnej obsługi weryfikacji (usługa płatna).
  - Human-in-the-loop: Jarvis przygotuje cały proces, wyświetli kroki do ręcznego potwierdzenia (np. potwierdź CAPTCHA,
    wklej kod SMS) i klikniesz/udostępnisz dane ręcznie.

Co mogę zrobić teraz — wybierz jedną z opcji:
A) Zmerguję ten branch do Twojego repo (stworzony branch feature/jarvis-improvements) — już utworzone zmiany.
B) Dodać prosty model_router.py i zintegrować go z agent.py, implementując retry/backoff i prosty priorytet providerów.
C) Zaimplementować prostą pamięć wektorową (SQLite + embedding offline) — może wymagać dodatkowych bibliotek.
D) Przygotować plan krok-po-kroku jak zbudować UI (okienkową aplikację Electron/PyQT) z animowaną „głową” i audio.

Jeśli chcesz, mogę teraz automatycznie wprowadzić także opcję B (router modeli) i drobną integrację w agent.py.
Napisz którą opcję wybierasz (A/B/C/D) albo opisz inną. 
