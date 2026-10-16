#!/usr/bin/env python3
"""Bezpieczne zapisanie kluczy Binance Testnet do vaulta.
Uruchom: python setup_testnet_keys.py
Klucze nie sa zapisywane w historii bash ani w plikach tekstowych.
"""
import sys
import getpass

sys.path.insert(0, "skills")
import vault_manager as vm

print("=== Zapisywanie kluczy Binance Testnet do vaulta ===")
print("(klucze sa szyfrowane AES-256, nie zapisza sie w historii bash)")
print()

api_key = getpass.getpass("Podaj BINANCE TESTNET API KEY: ").strip()
secret = getpass.getpass("Podaj BINANCE TESTNET SECRET: ").strip()

if not api_key or not secret:
    print("BLAD: puste klucze, przerwano.")
    sys.exit(1)

print()
print(vm.save_secret("BINANCE_TESTNET_API_KEY", api_key))
print(vm.save_secret("BINANCE_TESTNET_SECRET", secret))
print()
print("Zapisane sekrety w vaultcie:", vm.list_secrets())
print()
print("Test odczytu:")
print("  API KEY (pierwsze 8):", vm.get_secret("BINANCE_TESTNET_API_KEY")[:8], "...")
print("  SECRET (pierwsze 4):", vm.get_secret("BINANCE_TESTNET_SECRET")[:4], "...")