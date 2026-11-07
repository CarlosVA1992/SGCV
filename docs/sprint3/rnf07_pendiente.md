# RNF-07 — Backups diarios (RPO ≤24 h): pendiente para versión futura

## Requisito original
Configurar una tarea programada (cron) que ejecute un dump de la base de datos
diariamente a las 23:00, con procedimiento de restauración documentado y
verificable en menos de 2 horas.

## Decisión del Sprint 3
El requisito se pospone para una versión futura por limitantes técnicas del
hosting actual.

## Justificación técnica
- El proyecto está desplegado en **Render (plan free)**.
- Render free **no ofrece cron jobs persistentes**; solo permite "Cron Jobs"
  en planes de pago.
- Ejecutar un backup desde un proceso externo (GitHub Actions, servicio de
  terceros) requeriría credenciales de acceso a la base de datos SQLite del
  contenedor, que en Render free **no persiste entre despliegues**.
- La base de datos SQLite vive dentro del contenedor efímero; al redesplegar
  se pierde. Un backup real requiere migrar a PostgreSQL (plan de pago o
  servicio externo como Supabase/Neon).

## Alternativas evaluadas
| Alternativa | Viabilidad | Motivo de descarte |
|-------------|------------|--------------------|
| Cron Job de Render | ❌ | Solo en planes de pago |
| GitHub Actions con dump | ❌ | No hay acceso persistente a la BD SQLite del contenedor |
| Servicio externo (cron-job.org) | ❌ | Requiere endpoint público que exponga el dump (riesgo de seguridad) |
| Migrar a PostgreSQL + backup gestionado | ✅ | Requiere plan de pago o servicio externo; se evalúa en versión futura |

## Recomendación para versión futura
1. Migrar la base de datos a PostgreSQL (Render Postgres, Supabase o Neon).
2. Usar el backup automático del proveedor de PostgreSQL, o configurar
   `pg_dump` diario vía Cron Job de Render (plan de pago).
3. Documentar el procedimiento de restauración y probarlo con un dump real.

## Impacto en el proyecto
- RNF-07 queda como deuda técnica documentada.
- No afecta la funcionalidad del sistema en el Sprint 3.
- Se menciona explícitamente en el Sprint Review como limitación conocida.