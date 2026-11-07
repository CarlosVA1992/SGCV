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

## Cumplimiento normativo
Ver [`docs/cumplimiento_RD-01.md`](docs/cumplimiento_RD-01.md) para el detalle de protección de datos (CPE Art. 130–131 y Ley N.º 164).

## Puesta en marcha
Ver [`docs/setup.md`](docs/setup.md).


## Sprint 2 — Evidencia
- [Review y retrospectiva](docs/sprint2/review.md)
- [Revisión de código](docs/sprint2/revision_codigo.md)
- [Buffer de imprevistos](docs/sprint2/buffer.md)
- [Rendimiento RNF-01](docs/sprint2/rendimiento.md)
- [Usabilidad RNF-03](docs/sprint2/usabilidad.md)
- [Responsive RNF-06](docs/sprint2/responsive.md)
- [Identidad visual](docs/design/estilo.md)

## Deuda técnica conocida
- **RNF-07 (backups diarios):** pospuesto para versión futura por limitantes del
  hosting gratuito. Ver [`docs/sprint3/rnf07_pendiente.md`](docs/sprint3/rnf07_pendiente.md).