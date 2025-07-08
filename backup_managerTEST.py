import sys  # lire les arg passés en ligne de commande
import os  # manipuler les fichirs, dossiers et processus
import subprocess  # démarrer d'autres scripts ou processus
import datetime  # récupérer la date et l'heure actuelle
import signal  # envoyer des signaux à des processus

# Constante de configuration, stock des valeurs qui ne doivent pas être modifiées pendant l'exécution d'un programme
LOG_DIR = "./logs"  # là où seront stockés les logs
LOG_FILE = os.path.join(
    LOG_DIR, "backup_manager.log"
)  # chemin complet vers le fichier log
SCHEDULES = (
    "backup_schedules.txt"  # fichier texte contenant les plannings de sauvegarde
)
SERVICE_SCRIPT = "backup_service.py"  # script du service de sauvegarde à lancer
PID_FILE = "./backup_service.pid"  # fichier qui stocke l'identifiant (PID) du processus backup_service.py


def log(message):
    ts = datetime.datetime.now().strftime(
        "[%d/%m/%Y %H:%M]"
    )  # génère un horodatage dans le format [dd/mm/yyyy ; hh:mm]
    os.makedirs(
        LOG_DIR, exist_ok=True
    )  # garantit que le répertoire spécifié par log_dir existe, sinon il le crée, exist_ok=true empêche une erreur si le répertoire existe déjà
    with open(
        LOG_FILE, "a"
    ) as f:  # ouvre le fichier spécifié par log_file en mode annexe ('a'), un nouveau contenu est ajouté à la fin du fichier sans écraser le contenu existant
        f.write(
            f"{ts} {message}\n"
        )  # écrit l'horodatage et le message dans le fichier puis retour à la ligne


def is_running():  # vérifie si le fichier PID existe
    if os.path.exists(PID_FILE):  # ouvre le fichier en lecture
        with open(
            PID_FILE
        ) as f:  # lit le PID depuis le fichier et le convertit en entier, strip() supprime les espaces ou sauts de ligne
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)  # os.kill avec le signal 0 ne tue pas le processus
            return pid  # il sert à tester si le processus avec ce PID est encore actif et retourne PID s'il n'y a pas d'erreur
        except OSError:  # si aucun OSError n'est levé, alors le processus est en cours
            os.remove(
                PID_FILE
            )  # si le processus n'existe plus, une exception est levée, on supp le fichier PID car il est invalide
    return None  # si le fichier PID n'existe pas ou que le processus n'est pas actif, on retourne None


def start_service():
    if is_running():
        log("Error: backup_service already running")
        return
    try:
        proc = subprocess.Popen(
            [sys.executable, SERVICE_SCRIPT], start_new_session=True
        )
        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))
        log("backup_service started")
    except Exception as e:
        log(f"Error: can't start backup_service ({e})")


def stop_service():
    pid = is_running()
    if not pid:
        log("Error: backup_service not running")
        return
    try:
        os.kill(pid, signal.SIGTERM)
        os.remove(PID_FILE)
        log("backup_service stopped")
    except Exception as e:
        log(f"Error: can't stop backup_service ({e})")


def create_schedule(arg):
    parts = arg.split(";")
    if len(parts) != 3 or not parts[0] or not parts[1] or not parts[2]:
        log(f"Error: malformed schedule: {arg}")
        return
    with open(SCHEDULES, "a") as f:
        f.write(arg + "\n")
    log(f"New schedule added: {arg}")


def list_schedules():
    if not os.path.exists(SCHEDULES):
        log("Error: can't find backup_schedules.txt")
        return
    log("Show schedules list")
    with open(SCHEDULES) as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        print(f"{idx}: {line.strip()}")


def delete_schedule(arg):
    if not os.path.exists(SCHEDULES):
        log("Error: can't find backup_schedules.txt")
        return
    try:
        idx = int(arg)
        with open(SCHEDULES) as f:
            lines = f.readlines()
        if idx < 0 or idx >= len(lines):
            raise IndexError
        deleted = lines.pop(idx).strip()
        with open(SCHEDULES, "w") as f:
            f.writelines(lines)
        log(f"Schedule at index {idx} deleted")
    except (ValueError, IndexError):
        log(f"Error: can't find schedule at index {arg}")


def show_backups():
    backup_dir = "./backups"
    if not os.path.isdir(backup_dir):
        log("Error: can't find backups directory")
        return
    log("Show backups list")
    for name in os.listdir(backup_dir):
        print(name)


def main():
    if len(sys.argv) < 2:
        print("Usage: backup_manager.py <command> [args]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "start":
        start_service()
    elif cmd == "stop":
        stop_service()
    elif cmd == "create" and len(sys.argv) == 3:
        create_schedule(sys.argv[2])
    elif cmd == "list":
        list_schedules()
    elif cmd == "delete" and len(sys.argv) == 3:
        delete_schedule(sys.argv[2])
    elif cmd == "backups":
        show_backups()
    else:
        print("Unknown command or missing argument")
        sys.exit(1)


if __name__ == "__main__":
    main()
