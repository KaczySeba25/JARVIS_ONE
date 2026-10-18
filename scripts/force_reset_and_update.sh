#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$HOME/jarvis_backup_$(date +%Y%m%d_%H%M%S)"

echo "UWAGA: Ten skrypt nadpisze lokalne zmiany w repo JARVIS_ONE i usunie nieśledzone pliki."
echo "Tworzę kopię zapasową potencjalnie ważnych plików w: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup specific files if they exist
for f in agent.py requirements.txt install_fix.py; do
  if [ -e "$REPO_DIR/$f" ]; then
    echo "Kopiuję $f -> $BACKUP_DIR/"
    cp -a "$REPO_DIR/$f" "$BACKUP_DIR/" || true
  fi
done

cd "$REPO_DIR"

echo "Resetuję zmiany i usuwam nieśledzone pliki..."
git reset --hard
 git clean -fd

echo "Pobieram aktualizacje z remote..."
git pull

echo "Uruchamiam bootstrap (instalacja zależności i konfiguracja .env)..."
if [ -f scripts/bootstrap_agent.py ]; then
  python3 scripts/bootstrap_agent.py
else
  echo "Nie znaleziono scripts/bootstrap_agent.py — przerwanie."
  exit 1
fi

echo "Bootstrap zakończony. Aby uruchomić agenta, wykonaj: python3 agent.py"

echo "Jeśli wystąpiły błędy, wklej tutaj zawartość pliku data_vault/llm_errors.log i output terminala."
