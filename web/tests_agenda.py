from datetime import date, time, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Cita, Cliente, Mascota, Veterinario
from core.services import cambiar_estado


class AgendaTests(TestCase):
    def setUp(self):
        grupo, _ = Group.objects.get_or_create(name="recepcionista")
        self.user = User.objects.create_user(
            username="recepcion", password="clave123"
        )
        self.user.groups.add(grupo)
        self.client.login(username="recepcion", password="clave123")

        self.cliente = Cliente.objects.create(nombre="Ana", telefono="70000000")
        self.mascota = Mascota.objects.create(
            nombre="Firulais", especie="Perro", cliente=self.cliente
        )
        self.vet1 = Veterinario.objects.create(nombre="Dra. Vargas")
        self.vet2 = Veterinario.objects.create(nombre="Dr. Rojas")
        self.manana = date.today() + timedelta(days=1)

    def _crear_cita(self, vet, hora="10:00", fecha=None):
        return Cita.objects.create(
            cliente=self.cliente, mascota=self.mascota, veterinario=vet,
            fecha=fecha or self.manana, hora=time.fromisoformat(hora),
            motivo="Control", tipo="consulta",
        )

    # --- Transiciones ---

    def test_transicion_valida_programada_a_en_atencion(self):
        cita = self._crear_cita(self.vet1)
        cambiar_estado(cita, "en_atencion")
        cita.refresh_from_db()
        self.assertEqual(cita.estado, "en_atencion")

    def test_transicion_invalida_desde_cancelada(self):
        cita = self._crear_cita(self.vet1)
        cambiar_estado(cita, "cancelada")
        with self.assertRaises(ValueError):
            cambiar_estado(cita, "en_atencion")

    # --- Liberación de cupo ---

    def test_cancelar_libera_cupo(self):
        cita = self._crear_cita(self.vet1)
        cambiar_estado(cita, "cancelada")
        # Mismo cupo puede reservarse
        nueva = self._crear_cita(self.vet1)
        self.assertNotEqual(cita.id, nueva.id)
        self.assertEqual(Cita.objects.count(), 2)

    def test_doble_cita_activa_bloqueada(self):
        self._crear_cita(self.vet1)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            self._crear_cita(self.vet1)

    # --- Filtro por veterinario ---

    def test_filtro_por_veterinario(self):
        self._crear_cita(self.vet1, hora="10:00")
        self._crear_cita(self.vet2, hora="11:00")
        response = self.client.get(
            reverse("agenda"), {"fecha": self.manana.isoformat(),
                                "veterinario": self.vet1.id}
        )
        self.assertEqual(response.status_code, 200)
        citas_dia = response.context["citas_dia"]
        self.assertEqual(len(citas_dia), 1)
        self.assertEqual(citas_dia[0].veterinario, self.vet1)

    def test_agenda_muestra_citas_del_dia(self):
        self._crear_cita(self.vet1)
        response = self.client.get(
            reverse("agenda"), {"fecha": self.manana.isoformat()}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Firulais")