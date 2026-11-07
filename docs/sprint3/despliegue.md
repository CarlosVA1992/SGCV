# Despliegue y monitoreo — RNF-02

## Hosting
- Plataforma: Render (plan free)
- URL: https://huellitas.onrender.com
- Runtime: Python 3.12
- Servidor WSGI: gunicorn
- Build: `pip install -r requirements.txt && python manage.py migrate && python manage.py crear_roles`
- Start: `gunicorn config.wsgi --bind 0.0.0.0:$PORT`

## Variables de entorno
- `DEBUG=False`
- `ALLOWED_HOSTS=https://huellitas-yw64.onrender.com`
- `SECRET_KEY=<configurada en Render>`
- `PYTHON_VERSION=3.12.3`

## Monitoreo de uptime
- Servicio: UptimeRobot
- URL monitoreada: https://huellitas.onrender.com/login/
- Intervalo: 5 minutos
- Objetivo: ≥99% en horario laboral (lun–sáb 9:00–19:00)

## Notas
- Render free duerme tras 15 min de inactividad; el chequeo cada 5 min de UptimeRobot lo mantiene activo.
- La medición formal se hace durante el período de prueba del sprint (ver `uptime.md`).