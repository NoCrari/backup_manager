import os
import time
import datetime
import tarfile
from outils import CONF, log, init_dir

#       INITIALISATION DES REPERTOIRES

init_dir()

#       COMMANDES

def read_schedules():
    schedules = []
    try:
        with open(CONF["SCHEDULES_FILE"], 'r') as f:
            for line in f:
                parts = line.strip().split(';')
                if len(parts) == 3:
                    path, time_str, backup_name = parts
                    schedules.append((path, time_str, backup_name))
    except FileNotFoundError:
        log("Error: can't find backup_schedules.txt", "service")
    return schedules

def create_backup(source_path, backup_name):
    try:
        tar_path = os.path.join(CONF["BACKUP_DIR"], f"{backup_name}.tar")
        with tarfile.open(tar_path, "w") as tar:
            tar.add(source_path, arcname=os.path.basename(source_path))
        log(f"Backup done for {source_path} in backups/{backup_name}.tar", "service")
    except Exception as e:
        log(f"Error: can't backup {source_path} -> {e}", "service")

def main():
    done_for_minute = set()
    prev_minute = None

    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        if now != prev_minute:
            done_for_minute.clear()
            prev_minute = now

        schedules = read_schedules()

        for path, scheduled_time, backup_name in schedules:
            key = f"{scheduled_time}|{path}|{backup_name}"

            if scheduled_time == now and key not in done_for_minute:
                if os.path.exists(path):
                    create_backup(path, backup_name)
                else:
                    log(f"Error: path {path} does not exist", "service")
                done_for_minute.add(key)

        time.sleep(45)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f"Error: backup_service crashed -> {e}", "service")