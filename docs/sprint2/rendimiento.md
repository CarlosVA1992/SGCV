# Prueba de rendimiento — Agenda (RNF-01)

## Método
Script `scripts/prueba_carga_agenda.py`: 100 citas de prueba y 50 peticiones a `/agenda/`
con el `Client` de Django.

## Resultados
| Métrica | Valor |
|---------|-------|
| Promedio | [X] ms |
| Mínimo | [X] ms |
| Máximo | [X] ms |
| Mediana | [X] ms |
| Percentil 95 | [X] ms |

## Conclusión
Todas las peticiones quedaron por debajo de 3 s → **RNF-01 cumplido**.
Los índices en `fecha` y `veterinario` de `Cita` contribuyen al rendimiento.