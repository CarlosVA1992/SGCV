# Backups y restauración — RNF-07

## Estado: parcialmente cumplido

RNF-07 pide un backup automático diario (RPO ≤24 h). El plan free de PythonAnywhere
no incluye tareas programadas, por lo que el backup no puede automatizarse sin
exponer un endpoint público o pagar un plan superior. Se implementó un backup
**manual asistido** desde el admin, con procedimiento de restauración documentado
y probado.

## Implementación
- Script: `scripts/backup_db.sh` (copia consistente con `sqlite3 .backup`).
- Botón en el admin: `/admin/` → "Ejecutar backup ahora" (solo staff).
- Directorio de backups: `~/backups_huellitas/`.
- Rotación: últimos 7 backups.

## Frecuencia recomendada
- Ejecutar el backup **al final de cada jornada laboral** (idealmente 23:00).
- Ejecutar antes de cada despliegue o cambio importante.
- La persona responsable (administrador) debe hacerlo como parte del cierre diario.

## Procedimiento de restauración (verificable en <2 h)
1. Identificar el backup más reciente:
   ```bash
   ls -1t ~/backups_huellitas/*.sqlite3 | head -1