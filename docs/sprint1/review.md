# Sprint Review — Sprint 1

## Fecha
[completar]

## Asistentes
- Andrés Huansberg
- Daniel Conde
- Shomara Micaela Vargas (cliente)

## Objetivo del sprint
Dejar operativa la base segura del sistema: autenticación con roles, estructura multicapa
y registro de citas con validación anti-doble-cita.

## Demostración realizada
1. Login con usuario/contraseña y redirección según rol.
2. Registro de cita válida.
3. Rechazo de fecha pasada, hora fuera de horario, domingo y doble cita.
4. Bloqueo de recepcionista en vista clínica (403).
5. Registro automático en auditoría de login y creación de cita.

## Requisitos cerrados
- REQ-01 Registro de citas con validación
- REQ-06 Autenticación y roles (sin adenda)
- RNF-04 Acceso autenticado por rol
- RNF-05 Arquitectura multicapa (por convención)
- RD-01 Protección de datos (checklist)
- RD-02 Trazabilidad de acciones críticas

## Deuda técnica acordada para Sprint 2
- Adenda de corrección (REQ-06)
- Medición formal de rendimiento (RNF-01)
- Política de confidencialidad firmada (RD-01)
- Pantalla de consulta clínica (REQ-04)

## Feedback de la cliente
[completar]