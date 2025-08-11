# Backup Manager

Un système de sauvegarde automatisé en Python permettant de planifier et d'exécuter des sauvegardes de fichiers et dossiers selon un horaire défini.

## Description du projet

Le Backup Manager est composé de deux scripts principaux qui permettent de gérer un service de sauvegarde automatisé :

- **backup_manager.py** : Script d'orchestration pour gérer le service de sauvegarde
- **backup_service.py** : Service en arrière-plan qui exécute les sauvegardes planifiées
- **outils.py** : Module utilitaire contenant la configuration et les fonctions communes

## Fonctionnalités

### Gestion du service
- Démarrage et arrêt du service de sauvegarde en arrière-plan
- Vérification de l'état du service via fichier PID
- Logs détaillés de toutes les opérations

### Planification des sauvegardes
- Création de planifications de sauvegarde avec format `chemin;heure:minutes;nom_sauvegarde`
- Affichage de la liste des sauvegardes planifiées
- Suppression de planifications par index
- Sauvegarde automatique au format TAR

### Monitoring
- Affichage des fichiers de sauvegarde créés
- Logs séparés pour le manager et le service
- Gestion d'erreurs complète avec try/except

## Prérequis

- Python 3.x
- Modules Python standard : `os`, `sys`, `subprocess`, `signal`, `time`, `datetime`, `tarfile`
- Système d'exploitation Unix/Linux (pour la gestion des processus)

## Installation

1. Clonez ou téléchargez les fichiers du projet
2. Assurez-vous que tous les scripts sont dans le même répertoire
3. Rendez les scripts exécutables (optionnel) :
   ```bash
   chmod +x backup_manager.py backup_service.py
   ```

## Structure du projet

```
backup-manager/
├── backup_manager.py      # Script principal d'orchestration
├── backup_service.py      # Service de sauvegarde en arrière-plan
├── outils.py             # Module utilitaire et configuration
├── backup_schedules.txt  # Fichier des planifications (créé automatiquement)
├── backup_service.pid    # Fichier PID du service (créé automatiquement)
├── logs/                 # Répertoire des logs (créé automatiquement)
│   ├── backup_manager.log
│   └── backup_service.log
└── backups/              # Répertoire des sauvegardes (créé automatiquement)
    └── *.tar
```

## Utilisation

### Commandes du backup_manager.py

```bash
python3 backup_manager.py <command> [args]
```

#### Commandes disponibles

**Démarrer le service :**
```bash
python3 backup_manager.py start
```

**Arrêter le service :**
```bash
python3 backup_manager.py stop
```

**Créer une planification :**
```bash
python3 backup_manager.py create "chemin_source;heure:minutes;nom_sauvegarde"
```
Exemple :
```bash
python3 backup_manager.py create "test;16:07;backup_test"
```

**Lister les planifications :**
```bash
python3 backup_manager.py list
```

**Supprimer une planification :**
```bash
python3 backup_manager.py delete <index>
```

**Afficher les sauvegardes :**
```bash
python3 backup_manager.py backups
```

### Exemple d'utilisation complète

```bash
# Créer plusieurs planifications
python3 backup_manager.py create "test;16:07;backup_test"
python3 backup_manager.py create "documents;16:08;docs_backup"
python3 backup_manager.py create "photos;16:09;photos_backup"

# Afficher les planifications
python3 backup_manager.py list

# Démarrer le service
python3 backup_manager.py start

# Vérifier les sauvegardes créées
python3 backup_manager.py backups

# Arrêter le service
python3 backup_manager.py stop
```

## Format des planifications

Les planifications suivent le format : `chemin_source;heure:minutes;nom_sauvegarde`

- **chemin_source** : Chemin vers le fichier ou dossier à sauvegarder
- **heure:minutes** : Horaire d'exécution (format 24h, ex: 16:07)
- **nom_sauvegarde** : Nom du fichier de sauvegarde (sans extension)

## Logs

Le système génère des logs détaillés dans le répertoire `./logs/` :

- `backup_manager.log` : Actions du gestionnaire de sauvegarde
- `backup_service.log` : Actions du service en arrière-plan

Format des logs : `[dd/mm/yyyy hh:mm] message`

### Exemples de logs

**backup_manager.log :**
```
[13/02/2023 16:07] New schedule added: test;16:07;backup_test
[13/02/2023 16:07] backup_service started
[13/02/2023 16:08] backup_service stopped
```

**backup_service.log :**
```
[13/02/2023 16:07] Backup done for test in backups/backup_test.tar
[13/02/2023 16:08] Error: path documents does not exist
```

## Gestion d'erreurs

Le système inclut une gestion complète des erreurs :

- Vérification de l'existence des chemins source
- Validation du format des planifications
- Gestion des conflits de processus
- Logs détaillés des erreurs avec messages explicites

### Messages d'erreur courants

- `Error: Service already running` - Le service est déjà en cours d'exécution
- `Error: backup_service not running` - Tentative d'arrêt d'un service non actif
- `Error: malformed schedule` - Format de planification incorrect
- `Error: path does not exist` - Chemin source inexistant

## Configuration

La configuration est centralisée dans `outils.py` via le dictionnaire `CONF` :

```python
CONF = {
    "LOG_DIR": "./logs",
    "LOG_FILE_MANAGER": "./logs/backup_manager.log",
    "LOG_FILE_SERVICE": "./logs/backup_service.log",
    "SCHEDULES_FILE": "backup_schedules.txt",
    "BACKUP_DIR": "./backups",
    "SERVICE_SCRIPT": "backup_service.py",
    "PID_FILE": "./backup_service.pid",
}
```

## Limitations et notes importantes

- Le service vérifie les planifications toutes les 45 secondes
- Les sauvegardes sont au format TAR non compressé
- Une seule sauvegarde par minute par planification
- Nécessite un système Unix/Linux pour la gestion des processus
- Les répertoires de logs et sauvegardes sont créés automatiquement

## Résultats des tests

Le système a été testé et validé selon les critères suivants :
- ✅ Création et gestion des planifications
- ✅ Démarrage/arrêt du service en arrière-plan
- ✅ Exécution automatique des sauvegardes
- ✅ Gestion d'erreurs avec try/except
- ✅ Logs détaillés de toutes les opérations
- ✅ Validation des formats d'entrée
- ✅ Gestion des cas d'erreur (fichiers inexistants, service déjà démarré, etc.)

## Support et dépannage

En cas de problème :

1. Vérifiez les logs dans `./logs/`
2. Assurez-vous que les chemins source existent
3. Vérifiez le format des planifications
4. Contrôlez l'état du service avec `ps -ef | grep backup_service`

Pour un environnement propre, utilisez :
```bash
rm -rf logs backups backup_schedules.txt backup_service.pid
```
