# Onboarding: Nauka Tradingu i AI‑Agentów do Tradingu

Cel: Jarvis ma autonomicznie nauczyć się i zbudować fundamenty do pracy nad strategiami tradingowymi i agentami AI (testnety, backtesty, execution layer), zaczynając od researchu i planu działań.

Co Jarvis zrobi automatycznie (pierwsze kroki):
1. Research: uruchomi skills/trading_research.py aby zebrać i podsumować kluczowe źródła (artykuły, repo, tutoriale, API docs, testnety).
2. Plan: stworzy plan nauki i wdrożenia podzielony na moduły: dane, backtest, strategie, execution, monitoring, bezpieczeństwo.
3. Środowisko: sprawdzi i zainstaluje brakujące pakiety (self_repair.ensure_packages), utworzy strukturę katalogów (data_vault/, backtests/, notebooks/).
4. Dane: znajdzie darmowe źródła danych (Kaggle, publiczne API, giełdowy testnet), pobierze próbki i zapisze do `data_vault/datasets/`.
5. Proof‑of‑Concept: wygeneruje prosty backtester POC (skrypt) i przetestuje jedną prosta strategię na historycznych danych (paper trading / testnet only).
6. AI‑Agent design: przygotuje pipeline dla agenta (feature extraction → model → decyzja → execution) i zasugeruje algorytmy (ML/MLP, RL, heurystyki).
7. Audyt i pamięć: zapisze wszystkie wnioski, referencje i rezultaty do `semantic_memory` oraz `data_vault/logs/`.

Jak uruchomić inicjalny research (lokalnie / Codespaces):
- Aktywuj środowisko i zainstaluj zależności jak w README.
- Uruchom Jarvis Core: `python jarvis_core.py`
- Wpisz (przykład):
  Załóż polecenie: `Naucz się tradingu i agentów AI do tradingu` lub wywołaj skill:
  [RUN_SKILL: trading_research | trading basics, algorithmic trading, backtesting frameworks, ccxt, testnet]

Po tym etapie Jarvis zwróci podsumowanie i zaproponuje plan działań z etapami kolejnych zadań.

Bezpieczeństwo:
- Domyślnie testnet i paper‑trading; Jarvis nie wykona realnych zleceń bez Twojego wyraźnego potwierdzenia i kluczy API.
- Wszystkie klucze zapisuje w vault_manager (data_vault/vault.json) i nie wysyła ich nigdzie.

Następne kroki (po zakończeniu researchu):
- Zbieranie danych i uruchomienie POC backtestera
- Implementacja prostego agenta decyzyjnego i ocena wyników
- Integracja z testnetami giełd (CCXT/Exchange APIs) i monitorowanie

Jeśli chcesz, mogę teraz od razu uruchomić research (wygenerować plan i zacząć pobierać pierwsze dokumenty). Odpowiedz: "Uruchom research" aby kontynuować.
