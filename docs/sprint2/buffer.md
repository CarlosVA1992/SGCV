# Buffer de imprevistos — Sprint 2

## Imprevistos ocurridos
- Error `TransactionManagementError` al capturar `IntegrityError` en `crear_cita` → resuelto con `with transaction.atomic()`.
- `DisallowedHost: testserver` en el script de carga → resuelto agregando `testserver` a `ALLOWED_HOSTS`.
- Solo se crearon 70 de 100 citas en la prueba de carga por choques con el constraint → aceptable para la medición.
- Archivos de tareas anteriores quedaron sin commitear → se resolvió con commits separados.

## Lecciones
- Envolver siempre el `save()` que puede violar constraints en su propio `atomic`.
- Revisar `git status` antes de cada commit para no arrastrar pendientes.
- Para pruebas de carga, variar más las horas si se quiere crear el 100% de los registros.