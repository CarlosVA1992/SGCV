# Puesta en marcha del proyecto

## Requisitos
- Python 3.10+
- Git

## Instalación

    python -m venv venv
    source venv/bin/activate          # Linux/macOS
    venv\Scripts\activate             # Windows
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py crear_roles
    python manage.py createsuperuser

## Ejecución

    python manage.py runserver

Abrir http://127.0.0.1:8000/login/

## Roles
- administrador
- veterinario
- recepcionista

Asignar grupos desde /admin/ → Users.

## Migraciones

    python manage.py makemigrations
    python manage.py migrate

Las migraciones versionadas viven en `core/migrations/`. Para reproducir la BD desde cero: borrar `db.sqlite3` y correr `migrate`.