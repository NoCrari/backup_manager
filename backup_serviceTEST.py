import os
import time
import tarfile
import logging
import signal
from datetime import datetime

# === Chemins et constantes ===
SCHEDULE_FILE = "backup_schedules.txt"
BACKUP_DIR = "./backups"
LOG_DIR = "./logs"
LOG_FILE = os.path.join(LOG_DIR, "backup_service.log")

# === Préparation des dossiers ===
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# === Configuration des logs ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%d/%m/%Y %H:%M",
)


def log(msg):
    print(msg)
    logging.info(msg)


# === Gestion des signaux ===
running = True


def handle_stop(signum, frame):
    global running
    log("backup_service received stop signal")
    running = False


signal.signal(signal.SIGTERM, handle_stop)
signal.signal(signal.SIGINT, handle_stop)

# === Anti-doublons : suivi des sauvegardes exécutées cette minute ===
already_ran = set()


# === Fonction de sauvegarde ===
def perform_backup(path, name):
    try:
        archive_path = os.path.join(BACKUP_DIR, f"{name}.tar")
        with tarfile.open(archive_path, "w") as tar:
            tar.add(path, arcname=os.path.basename(path))
        log(f"Backup done for {path} in {archive_path}")
    except Exception as e:
        log(f"Error: failed to backup {path} → {e}")


# === Lecture et traitement des plannings ===
def check_schedules():
    now = datetime.now().strftime("%H:%M")
    global already_ran

    try:
        with open(SCHEDULE_FILE, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        log("Error: backup_schedules.txt not found")
        return

    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(";")
        if len(parts) != 3:
            log(f"Error: malformed schedule line: {line}")
            continue

        path, time_str, backup_name = parts
        unique_id = f"{path}|{time_str}|{backup_name}|{now}"

        if time_str == now and unique_id not in already_ran:
            perform_backup(path, backup_name)
            already_ran.add(unique_id)


# === Boucle principale ===
if __name__ == "__main__":
    log("backup_service launched")
    try:
        while running:
            check_schedules()
            time.sleep(45)
        log("backup_service terminated gracefully")
    except Exception as e:
        log(f"Error: backup_service crashed → {e}")
