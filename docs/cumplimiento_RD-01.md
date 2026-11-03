# Cumplimiento RD-01 — Protección de datos personales y clínicos

## Marco normativo
- Constitución Política del Estado (CPE), Art. 130–131
- Ley N.º 164 (Ley General de Telecomunicaciones, Tecnologías de Información y Comunicación)

## Medidas implementadas en el Sprint 1

| Medida | Implementación | Evidencia |
|--------|----------------|-----------|
| Cifrado de contraseñas | PBKDF2 nativo de Django | `web/tests_roles.py::PasswordHashTests` |
| Validadores de contraseña | `AUTH_PASSWORD_VALIDATORS` en `config/settings.py` | Configuración activa |
| Control de acceso por rol | Decorador `role_required` en `core/decorators.py` | `web/tests_roles.py::RoleAccessTests` |
| Datos clínicos restringidos | Rol recepcionista bloqueado en vistas clínicas | `test_recepcionista_no_accede_a_historial` |

## Política de confidencialidad (resumen)
- Solo usuarios autenticados acceden al sistema.
- Los datos clínicos son visibles únicamente para roles `administrador` y `veterinario`.
- Las contraseñas nunca se almacenan en texto plano.
- Toda acción crítica queda registrada en la tabla `Auditoria` (RD-02).

## Pendiente para sprints posteriores
- Cifrado en reposo de datos clínicos sensibles (si el hosting lo requiere).
- Política de confidencialidad formal firmada por la cliente.
- Revisión de cumplimiento al cierre del proyecto.