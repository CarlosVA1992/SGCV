# Backups y restauración — RNF-07

## Configuración
- Plataforma: PythonAnywhere (plan free)
- Script: `scripts/backup_db.sh`
- Tarea programada: diaria a las 23:00 (hora Bolivia = 03:00 UTC)
- Directorio de backups: `~/backups_huellitas/`
- Rotación: se conservan los últimos 7 backups
- RPO: ≤24 h (backup diario)

## Procedimiento de backup
1. PythonAnywhere ejecuta `bash ~/SGCV/scripts/backup_db.sh` diariamente.
2. El script usa `sqlite3 .backup` para copia consistente.
3. El archivo se guarda como `huellitas_YYYYMMDD_HHMMSS.sqlite3`.

## Procedimiento de restauración (verificable en <2 h)
1. Identificar el backup más reciente:
   ```bash
   ls -1t ~/backups_huellitas/*.sqlite3 | head -1
