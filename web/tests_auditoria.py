from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Auditoria, Cita, Cliente, Mascota, Veterinario


class AuditoriaTests(TestCase):
    def setUp(self):
        grupo, _ = Group.objects.get_or_create(name="recepcionista")
        self.user = User.objects.create_user(
            username="recepcion", password="clave123"
        )
        self.user.groups.add(grupo)

        self.cliente = Cliente.objects.create(nombre="Ana", telefono="70000000")
        self.mascota = Mascota.objects.create(
            nombre="Firulais", especie="Perro", cliente=self.cliente
        )
        self.vet = Veterinario.objects.create(nombre="Dra. Vargas")
        self.manana = date.today() + timedelta(days=1)

    def test_login_genera_registro_auditoria(self):
        self.assertEqual(Auditoria.objects.count(), 0)
        self.client.login(username="recepcion", password="clave123")
        self.assertEqual(Auditoria.objects.count(), 1)
        registro = Auditoria.objects.first()
        self.assertEqual(registro.accion, "login")
        self.assertEqual(registro.usuario, self.user)
        self.assertEqual(registro.registro_afectado, f"user:{self.user.id}")

    def test_crear_cita_genera_registro_auditoria(self):
        self.client.login(username="recepcion", password="clave123")
        Auditoria.objects.all().delete()  # limpia el login para aislar

        self.client.post(reverse("crear_cita"), {
            "cliente": self.cliente.id,
            "mascota": self.mascota.id,
            "veterinario": self.vet.id,
            "fecha": self.manana.isoformat(),
            "hora": "10:00",
            "motivo": "Control",
            "tipo": "consulta",
            "duracion_min": 30,
        })

        self.assertEqual(Cita.objects.count(), 1)
        self.assertEqual(Auditoria.objects.count(), 1)
        registro = Auditoria.objects.first()
        self.assertEqual(registro.accion, "cita_creada")
        cita = Cita.objects.first()
        self.assertEqual(registro.registro_afectado, f"cita:{cita.id}")
        self.assertEqual(registro.usuario, self.user)