from datetime import date, time

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import (
    Auditoria,
    Cita,
    Cliente,
    FranjaHoraria,
    Mascota,
    Veterinario,
)
from core.services import registrar_emergencia


class EmergenciaServiceTests(TestCase):
    """Tests del servicio registrar_emergencia."""

    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Ana", telefono="70000000")
        self.cliente2 = Cliente.objects.create(nombre="Luis", telefono="71111111")
        self.mascota = Mascota.objects.create(
            nombre="Firulais", especie="Perro", cliente=self.cliente
        )
        self.mascota2 = Mascota.objects.create(
            nombre="Michi", especie="Gato", cliente=self.cliente2
        )
        self.vet = Veterinario.objects.create(nombre="Dra. Vargas")
        self.hoy = date.today()

        # Cita a extender: 10:00, 30 min
        self.cita = Cita.objects.create(
            cliente=self.cliente, mascota=self.mascota,
            veterinario=self.vet, fecha=self.hoy, hora=time(10, 0),
            motivo="Control", tipo="consulta", duracion_min=30,
        )
        # Cita afectada: 11:00
        self.afectada = Cita.objects.create(
            cliente=self.cliente2, mascota=self.mascota2,
            veterinario=self.vet, fecha=self.hoy, hora=time(11, 0),
            motivo="Vacuna", tipo="consulta", duracion_min=30,
        )
        # Franja disponible para la propuesta
        FranjaHoraria.objects.create(
            veterinario=self.vet, dia_semana=self.hoy.weekday(),
            hora_inicio=time(9, 0), hora_fin=time(9, 30),
        )

    def test_emergencia_extiende_duracion(self):
        resultado = registrar_emergencia(self.cita.id, 15)
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.duracion_min, 45)
        self.assertEqual(resultado["minutos_extra"], 15)

    def test_emergencia_calcula_horas_fin(self):
        resultado = registrar_emergencia(self.cita.id, 15)
        self.assertEqual(resultado["hora_fin_original"], time(10, 30))
        self.assertEqual(resultado["hora_fin_nueva"], time(10, 45))

    def test_citas_afectadas_cambian_estado(self):
        registrar_emergencia(self.cita.id, 15)
        self.afectada.refresh_from_db()
        self.assertEqual(self.afectada.estado, "reprogramada")

    def test_cita_no_afectada_mantiene_estado(self):
        # Cita anterior a la extensión no debe cambiar
        anterior = Cita.objects.create(
            cliente=self.cliente, mascota=self.mascota,
            veterinario=self.vet, fecha=self.hoy, hora=time(9, 0),
            motivo="Anterior", tipo="consulta", duracion_min=30,
        )
        registrar_emergencia(self.cita.id, 15)
        anterior.refresh_from_db()
        self.assertEqual(anterior.estado, "programada")

    def test_listado_afectadas_incluye_telefono(self):
        resultado = registrar_emergencia(self.cita.id, 15)
        self.assertEqual(len(resultado["afectadas"]), 1)
        self.assertEqual(resultado["afectadas"][0].cliente.telefono, "71111111")

    def test_auditoria_registra_emergencia(self):
        registrar_emergencia(self.cita.id, 15)
        self.assertTrue(
            Auditoria.objects.filter(accion="emergencia_registrada").exists()
        )

    def test_auditoria_registra_reprogramacion_lote(self):
        registrar_emergencia(self.cita.id, 15)
        self.assertTrue(
            Auditoria.objects.filter(accion="citas_reprogramadas_lote").exists()
        )

    def test_sin_afectadas_no_reprograma(self):
        # Extender la última cita del día no afecta a nadie
        resultado = registrar_emergencia(self.afectada.id, 15)
        self.assertEqual(len(resultado["afectadas"]), 0)
        self.assertEqual(resultado["reprogramadas"], 0)


class EmergenciaViewTests(TestCase):
    """Tests de la vista /citas/<id>/emergencia/."""

    def setUp(self):
        g_vet, _ = Group.objects.get_or_create(name="veterinario")
        g_rec, _ = Group.objects.get_or_create(name="recepcionista")
        self.user_vet = User.objects.create_user(
            username="vet", password="clave123"
        )
        self.user_vet.groups.add(g_vet)
        self.user_rec = User.objects.create_user(
            username="rec", password="clave123"
        )
        self.user_rec.groups.add(g_rec)

        self.cliente = Cliente.objects.create(nombre="Ana", telefono="70000000")
        self.mascota = Mascota.objects.create(
            nombre="Firulais", especie="Perro", cliente=self.cliente
        )
        self.vet = Veterinario.objects.create(nombre="Dra. Vargas")
        self.cita = Cita.objects.create(
            cliente=self.cliente, mascota=self.mascota,
            veterinario=self.vet, fecha=date.today(), hora=time(10, 0),
            motivo="Control", tipo="consulta", duracion_min=30,
        )

    def test_veterinario_accede_a_emergencia(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(reverse("emergencia", args=[self.cita.id]))
        self.assertEqual(response.status_code, 200)

    def test_recepcionista_no_accede_a_emergencia(self):
        self.client.login(username="rec", password="clave123")
        response = self.client.get(reverse("emergencia", args=[self.cita.id]))
        self.assertEqual(response.status_code, 403)

    def test_post_emergencia_extiende_cita(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.post(
            reverse("emergencia", args=[self.cita.id]),
            {"minutos_extra": 15},
        )
        self.assertEqual(response.status_code, 200)
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.duracion_min, 45)

    def test_post_minutos_invalidos_no_extiende(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.post(
            reverse("emergencia", args=[self.cita.id]),
            {"minutos_extra": 0},
        )
        self.assertEqual(response.status_code, 200)
        self.cita.refresh_from_db()
        self.assertEqual(self.cita.duracion_min, 30)  # sin cambio