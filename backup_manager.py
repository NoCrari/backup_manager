import sys
import os
import subprocess
import signal
from outils import CONF, log, init_dir

#       INITIALISATION DES REPERTOIRES

init_dir()

#       PID (vérifie si le service est en cours et retourne le PID)

def get_pid_run():
    try:
        if os.path.exists(CONF["PID_FILE"]):
            with open(CONF["PID_FILE"]) as f:
                pid = int(f.read().strip())
                os.kill(pid, 0)
                return pid
    except (OSError, ValueError):
        try:
            os.remove(CONF["PID_FILE"])
        except:
            pass
    return None

#       LES COMMANDES 

#Lance backup_service en arrière-plan
def start_service():
    if get_pid_run():
        log("Error: Service already running", "manager")
        return
    try:
        proc = subprocess.Popen([sys.executable, CONF["SERVICE_SCRIPT"]], start_new_session=True)
        with open(CONF["PID_FILE"], 'w') as f:
            f.write(str(proc.pid))
        log("backup_service started", "manager")
    except Exception as e:
        log(f"Error: can't start backup_service ({e})", "manager")

#Stop la processus backup_service.py
def stop_service():
    pid = get_pid_run()
    if not pid:
        log("Error: backup_service not running", "manager")
        return
    try:
        os.kill(pid, signal.SIGTERM)
        os.remove(CONF["PID_FILE"])
        log("backup_service stopped", "manager")
    except Exception as e:
        log(f"Error: can't stop backup_service ({e})", "manager")

#Ajout d'une nouvelle ligne de planification dans backup_schedules.txt
def create_schedule(schedule):
    try:
        parts = schedule.split(';')
        if len(parts) != 3 or not all(parts):
            raise ValueError
        with open(CONF["SCHEDULES_FILE"], 'a') as f:
            f.write(schedule + '\n')
        log(f"New schedule added: {schedule}", "manager")
    except:
        log(f"Error: malformed schedule: {schedule}", "manager")

#Affiche la liste des sauvegardes planifiées
def list_schedules():
    try:
        if not os.path.exists(CONF["SCHEDULES_FILE"]):
            raise FileNotFoundError
        with open(CONF["SCHEDULES_FILE"]) as f:
            lines = f.readlines()
        log("Show schedules list", "manager")
        for idx, line in enumerate(lines):
            print(f"{idx}: {line.strip()}")
    except:
        log("Error: can't find backup_schedules.txt", "manager")

#Supprime une ligne dans backup_schedules.txt selon un index donné
def delete_schedule(index_string):
    try:
        if not os.path.exists(CONF["SCHEDULES_FILE"]):
            raise FileNotFoundError
        index = int(index_string)
        with open(CONF["SCHEDULES_FILE"], 'r') as f:
            lines = f.readlines()
        if index < 0 or index >= len(lines):
            raise IndexError
        lines.pop(index)
        with open(CONF["SCHEDULES_FILE"], 'w') as f:
            f.writelines(lines)
        log(f"Schedule at index {index} deleted", "manager")
    except FileNotFoundError:
        log("Error: can't find backup_schedules.txt", "manager")
    except:
        log(f"Error: can't find schedule at index {index_string}", "manager")

#Affiche les fichiers présents dans le dossier ./backups
def show_backups():
    try:
        if not os.path.isdir(CONF["BACKUP_DIR"]):
            raise FileNotFoundError
        log("Show backups list", "manager")
        for name in os.listdir(CONF["BACKUP_DIR"]):
            print(name)
    except:
        log("Error: can't find backups directory", "manager")


#       PRINCIPAL

def main():
    if len(sys.argv) < 2:
        print("Usage: backup_manager.py <command> [args]")
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "start": start_service,
        "stop": stop_service,
        "create": lambda: create_schedule(args[0]) if args else print("Missing schedule"),
        "list": list_schedules,
        "delete": lambda: delete_schedule(args[0]) if args else print("Missing index"),
        "backups": show_backups,
    }

    action = commands.get(cmd)
    if action:
        action()
    else:
        print("Unknown command")

if __name__ == '__main__':
    main()