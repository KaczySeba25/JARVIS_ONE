"""
Skill: system_info
Opis: Pobiera informacje o systemie operacyjnym, użytkowniku i wolnym miejscu na dysku.
"""
import os
import platform
import shutil

def run():
    os_name = platform.system()
    os_release = platform.release()
    machine = platform.machine()
    
    username = os.environ.get('USER', os.environ.get('USERNAME', 'Nieznany'))

    try:
        total, used, free = shutil.disk_usage('/')
        free_gb = free / (1024**3)
        total_gb = total / (1024**3)
        disk_info = f"Wolne: {free_gb:.2f} GB / Łącznie: {total_gb:.2f} GB"
    except Exception as e:
        disk_info = f"Błąd dysku: {e}"

    return f"System: {os_name} {os_release} ({machine}) | Użytkownik: {username} | Dysk: {disk_info}"
