#!/bin/bash

echo "=== JARVIS GITHUB CLEANER ==="

cat > .gitignore << 'GITEOF'
.env
.env.*

__pycache__/
*.pyc
*.pyo

data_vault/vault.key
data_vault/vault.salt
data_vault/vault.enc
data_vault/memory.db

tiktok_infra/session.json

.vscode/
GITEOF

echo "[1/8] Czyszczenie cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "[2/8] Usuwanie sekretów z Git Index..."

git rm --cached .env 2>/dev/null || true
git rm --cached data_vault/vault.key 2>/dev/null || true
git rm --cached data_vault/vault.salt 2>/dev/null || true
git rm --cached data_vault/vault.enc 2>/dev/null || true
git rm --cached data_vault/memory.db 2>/dev/null || true
git rm --cached tiktok_infra/session.json 2>/dev/null || true

echo "[3/8] Dodawanie gitignore..."

git add .gitignore

echo "[4/8] Reset ostatniego commita..."

git reset --soft HEAD~1

echo "[5/8] Ponowne indeksowanie..."

git add .

echo "[6/8] Nowy commit..."

git commit -m "Security cleanup - remove secrets"

echo "[7/8] Force push..."

git push origin main --force

echo "[8/8] GOTOWE"

