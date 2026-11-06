# Sprint Planning — Sprint 3

## Contexto
- Sprint 1 y 2 cerrados. 33 tests en verde.
- Feedback de la cliente en Review S2: evolución clínica y modelo de optimización.
- Duración: 2 semanas. Capacidad: ~120 h.

## Objetivo
Entregar la vista de evolución clínica con resumen del paciente, el optimizador
de asignación que propone horarios automáticamente, la gestión de emergencias,
y la disponibilidad y backups en el hosting disponible.

## Respuestas de la cliente en planning
1. La evolución clínica NO incluye gráficos de peso.
2. Alergias y medicamentos activos son campos de `Mascota`.
3. El optimizador DEBE proponer horarios automáticamente.
4. SÍ hay hosting disponible para RNF-02 y RNF-07.

## Alcance seleccionado

| Requisito | Tareas | Horas |
|-----------|--------|-------|
| REQ-05 Evolución clínica | T-40 a T-44 | 22 |
| REQ-07 Optimización (propuesta automática) | T-45 a T-49 | 30 |
| REQ-03 Emergencias | T-50 a T-52 | 13 |
| RNF-02 Disponibilidad (despliegue real) | T-53, T-54 | 8 |
| RNF-07 Backups (cron real) | T-55, T-56 | 5 |
| Transversales | T-57 a T-59 | 16 |
| **Total** | | **94 h** |

## Orden de ejecución
1. REQ-05 (T-42 → T-40 → T-41 → T-43 → T-44)
2. REQ-07 (T-45 → T-46 → T-47 → T-48 → T-49)
3. REQ-03 (T-50 → T-51 → T-52), solo si T-48 está listo
4. RNF-02 y RNF-07 (T-53 a T-56)

## Definition of Done
- Código mergeado con revisión.
- Tests pasando (33 del S2 + nuevos).
- Migraciones reproducibles.
- Pantallas nuevas usan `base.html` y la paleta de `docs/design/estilo.md`.
- Documentación en `docs/sprint3/`.
- Demo en Sprint Review: evolución clínica, optimizador con propuesta automática, backups configurados.

## Riesgos
- REQ-07 es el bloque más complejo; si se desborda, se recorta REQ-03 a S4.
- RNF-02 y RNF-07 dependen del hosting; se ejecutan al final cuando el código está estable.

## Fuera de alcance
- Gráficos de peso en evolución.
- Alergias/medicamentos por consulta (son de mascota).
- REQ-07 afinado más allá de la propuesta automática básica (si queda tiempo, S4).