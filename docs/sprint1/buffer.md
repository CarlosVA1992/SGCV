# Buffer de imprevistos — Sprint 1

## Imprevistos ocurridos
- Doble carga aparente de señales (falso positivo: `_live_receivers` devuelve tupla).
- Doble guardado en `crear_cita` que duplicaba auditoría → corregido.
- README mal ubicado en `config/` → movido a raíz.

## Horas consumidas del buffer
[completar]

## Lecciones
- Verificar `_live_receivers(...)[0]` en lugar de `len(...)`.
- Un solo `save()` por flujo para no duplicar señales.