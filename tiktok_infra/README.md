# TikTok Infrastructure

## Status: WYMAGA DANYCH UWIERZYTELNIAJĄCYCH (Cookies/Tokens)

Zgodnie z zasadami bezpieczeństwa i moimi ograniczeniami technicznymi (brak dostępu do GUI), nie mogę samodzielnie zarejestrować konta.

### Instrukcja dla Sebastiana:
1.  Zaloguj się ręcznie na [TikTok](https://www.tiktok.com).
2.  Otwórz konsolę deweloperską (F12) -> zakładka "Network" -> odśwież stronę.
3.  Znajdź żądanie do API TikTok.
4.  Skopiuj nagłówki `Cookie` i `User-Agent`.
5.  Wklej je do pliku `session.json` w tym folderze.

### Struktura:
- `session.json`: Dane sesji (Cookies).
- `tiktok_client.py`: Klient API.
- `skill_tiktok.py`: Skill dla JARVIS.

## Jak używać:
Po wypełnieniu `session.json`, mogę użyć skilla `tiktok_manager` do:
- Pobierania profilu.
- Analizy trendów (jeśli API to pozwala).
- Przygotowywania treści.

**Uwaga:** Automatyczna rejestracja jest blokowana przez CAPTCHA i ToS. Ta infrastruktura służy do zarządzania istniejącym kontem.