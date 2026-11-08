# Medición de uptime — RNF-02

## Configuración del monitoreo
- Servicio: UptimeRobot (plan free)
- URL monitoreada: https://cva1992.pythonanywhere.com
- Intervalo de chequeo: 5 minutos
- Tipo: HTTP(s)
- Fecha de inicio de medición: [dd/mm/aaaa]

## Objetivo
Disponibilidad ≥99% en horario laboral (lun–sáb 9:00–19:00).

## Período de prueba
- Inicio: [07/11/2026 12:04]
- En curso

## Resultados
| Métrica | Valor |
|---------|-------|
| Uptime total | [X]% |
| Caídas detectadas | [N] |
| Duración total de caídas | [X] min |
| Estado actual | Up / Down |

## Log de caídas
| Fecha | Hora inicio | Hora fin | Duración | Causa |
|-------|-------------|----------|----------|-------|
| [dd/mm/aaaa] | [hh:mm] | [hh:mm] | [X] min | [motivo] |

> Si no hubo caídas, escribir: "No se registraron caídas durante el período de prueba."

## Conclusión
[Completar según los resultados: si el uptime fue ≥99%, RNF-02 se cumple en el período medido;
si hubo caídas por el sleep de Render free, documentar que el chequeo de UptimeRobot las mitigó.]

## Nota sobre Render free
El plan free de Render duerme el servicio tras 15 min de inactividad. El chequeo
cada 5 min de UptimeRobot mantiene el servicio activo, lo que mitiga el impacto
en la disponibilidad durante el horario laboral. Para producción real se
recomienda un plan de pago o un hosting sin sleep.