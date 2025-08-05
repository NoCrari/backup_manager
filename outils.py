import os 
import datetime

#       CONFIGURATION CENTRALE

CONF = {
    #Log
    "LOG_DIR": "./logs",
    "LOG_FILE_MANAGER": "./logs/backup_manager.log",
    "LOG_FILE_SERVICE": "./logs/backup_service.log",
    
    #Backup
    "SCHEDULES_FILE": "backup_schedules.txt",
    "BACKUP_DIR": "./backups",

    #Service
    "SERVICE_SCRIPT": "backup_service.py",
    "PID_FILE": "./backup_service.pid",  
}

#       CREATION DES REPERTOIRES

def init_dir(type_log="manager"):
    try:
        os.makedirs(CONF["LOG_DIR"], exist_ok=True)
        os.makedirs(CONF["BACKUP_DIR"], exist_ok=True)
    except Exception as e:
        log(f"Error: failed to create directories -> {e}", type_log)

#       INITIALISATION DES LOGS

def log(msg, type_log="manager"):
    log_file = CONF["LOG_FILE_MANAGER"] if type_log == "manager" else CONF["LOG_FILE_SERVICE"]

    ts = datetime.datetime.now().strftime("[%d/%m/%Y %H:%M]")
    try: 
        with open(log_file, 'a') as f:
            f.write(f"{ts} {msg}\n")
    except Exception as e:
        print(f"Logging failed: {e} - original message was: {msg}")