#!/bin/bash

backup_base_folder=$FRIENDLY_BET_BACKUP_FOLDER

if [[ -z $backup_base_folder ]]; then
  echo "Backup folder not found. Using default: /home/maddrum/pCloudDrive/friendly_bet/production_backup" >/dev/stderr
  backup_base_folder=/home/maddrum/pCloudDrive/friendly_bet/production_backup
fi
backup_folder="$backup_base_folder/$(date +%Y-%m-%d--%H-%M)"
mkdir "$backup_folder"

echo "[INFO] Copying db..."
ssh maddrum@ssh.pythonanywhere.com "cd /home/maddrum/friendly_bet \
                        && tar -cf - db.sqlite3 | gzip -9" >"$backup_folder/db_dump.tar.gz"
echo "[INFO] DB copied."

echo "[INFO] Completed successfully."
