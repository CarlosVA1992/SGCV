"""
Prueba de carga simple sobre la vista de agenda.
Mide el tiempo de respuesta de N peticiones a /agenda/ con datos de prueba.

Uso:
    python scripts/prueba_carga_agenda.py
"""

import os
import sys
import time
from datetime import date, timedelta

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import Group, User
from core.models import Cita, Cliente, Mascota, Veterinario


def preparar_datos(n_citas=100):
    grupo, _ = Group.objects.get_or_create(name="recepcionista")
    user, _ = User.objects.get_or_create(username="carga")
    user.set_password("clave123")
    user.save()
    user.groups.add(grupo)

    cliente, _ = Cliente.objects.get_or_create(
        nombre="Carga Test", defaults={"telefono": "70000000"}
    )
    mascota, _ = Mascota.objects.get_or_create(
        nombre="CargaMascota",
        defaults={"especie": "Perro", "cliente": cliente},
    )
    vet, _ = Veterinario.objects.get_or_create(nombre="Dr. Carga")

    hoy = date.today()
    creadas = 0
    for i in range(n_citas):
        fecha = hoy + timedelta(days=i % 7)
        hora = f"{9 + (i % 10):02d}:{(i % 2) * 30:02d}"
        try:
            Cita.objects.create(
                cliente=cliente, mascota=mascota, veterinario=vet,
                fecha=fecha, hora=hora,
                motivo="Carga", tipo="consulta",
            )
            creadas += 1
        except Exception:
            pass
    print(f"Citas creadas para la prueba: {creadas}")


def medir(n_peticiones=50):
    c = Client()
    c.login(username="carga", password="clave123")
    tiempos = []
    for _ in range(n_peticiones):
        inicio = time.perf_counter()
        r = c.get("/agenda/")
        fin = time.perf_counter()
        if r.status_code != 200:
            print(f"ERROR: status {r.status_code}")
            return
        tiempos.append((fin - inicio) * 1000)

    tiempos.sort()
    print(f"Peticiones: {n_peticiones}")
    print(f"Promedio: {sum(tiempos)/len(tiempos):.1f} ms")
    print(f"Mínimo: {tiempos[0]:.1f} ms")
    print(f"Máximo: {tiempos[-1]:.1f} ms")
    print(f"Mediana: {tiempos[len(tiempos)//2]:.1f} ms")
    print(f"Percentil 95: {tiempos[int(len(tiempos)*0.95)]:.1f} ms")

    if tiempos[-1] < 3000:
        print("OK: todas las peticiones < 3 s (RNF-01)")
    else:
        print("FALLO: alguna petición >= 3 s (RNF-01)")


if __name__ == "__main__":
    preparar_datos()
    medir()