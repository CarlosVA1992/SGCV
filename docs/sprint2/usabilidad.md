# Verificación RNF-03 — Cita en ≤5 pasos

## Flujo medido

| Paso | Acción | Pantalla / URL |
|------|--------|----------------|
| 1 | Iniciar sesión | `/login/` |
| 2 | Clic en "Nueva cita" en la nav | — |
| 3 | Completar formulario (cliente, mascota, veterinario, fecha, hora, motivo, tipo, duración) | `/citas/nueva/` |
| 4 | Guardar y ver mensaje de confirmación | misma pantalla |

**Total: 4 pasos/pantallas.**

## Resultado
El flujo cumple RNF-03 (≤5 pasos). Si se cuenta desde que el usuario ya está autenticado,
son 2 pasos (nav + formulario).

## Verificación manual
Prueba realizada con la recepcionista: [completar fecha]. Confirmó que el flujo
es directo y no requiere pantallas intermedias.