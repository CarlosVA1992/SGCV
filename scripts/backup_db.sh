#!/bin/bash
# Backup diario de la base de datos SQLite
# RNF-07: RPO <= 24 h

set -e

PROYECTO="$HOME/SGCV"
BACKUPS="$HOME/backups_huellitas"
FECHA=$(date +%Y%m%d_%H%M%S)
ARCHIVO="$BACKUPS/huellitas_$FECHA.sqlite3"

mkdir -p "$BACKUPS"

# Copia consistente usando el comando .backup de sqlite3
sqlite3 "$PROYECTO/db.sqlite3" ".backup '$ARCHIVO'"

# Conservar solo los últimos 7 backups (rotación)
ls -1t "$BACKUPS"/huellitas_*.sqlite3 | tail -n +8 | xargs -r rm --

echo "Backup creado: $ARCHIVO"