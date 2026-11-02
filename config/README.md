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