# Software de Gestion y Consultas de Veterinaria

Proyecto Django 5.x para historial clínico y agenda de citas.

## Estructura (arquitectura multicapa por convención)

- `config/` — configuración del proyecto
- `core/` — capa de datos + negocio (models, señales, decoradores, lógica)
- `web/` — capa de presentación (vistas, templates, formularios, urls)

## Convención de commits

Cada commit referencia la tarea del sprint backlog:

    T-XX: descripción corta en imperativo

## Entorno

- Python 3.10+
- Django 5.x
## Verificación RNF-04 — Acceso autenticado por rol

- Contraseñas hasheadas con PBKDF2 (nativo de Django).
- Validadores de contraseña activos (`AUTH_PASSWORD_VALIDATORS`).
- Control de acceso por rol mediante decorador `role_required` en capa de negocio.
- Tests: `web/tests_roles.py` cubre login, bloqueo por rol, anónimo redirigido y hash de contraseña.