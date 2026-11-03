from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse

from core.models import Cita, Cliente, Mascota, Veterinario


class CitaFormTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="Ana", telefono="70000000")
        self.mascota = Mascota.objects.create(
            nombre="Firulais", especie="Perro", cliente=self.cliente
        )
        self.vet = Veterinario.objects.create(nombre="Dra. Vargas")
        self.manana = date.today() + timedelta(days=1)

    def _post(self, **overrides):
        data = {
            "cliente": self.cliente.id,
            "mascota": self.mascota.id,
            "veterinario": self.vet.id,
            "fecha": self.manana.isoformat(),
            "hora": "10:00",
            "motivo": "Control",
            "tipo": "consulta",
            "duracion_min": 30,
        }
        data.update(overrides)
        return self.client.post(reverse("crear_cita"), data)

    def test_cita_valida_se_crea(self):
        response = self._post()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cita.objects.count(), 1)

    def test_fecha_pasada_rechazada(self):
        ayer = date.today() - timedelta(days=1)
        response = self._post(fecha=ayer.isoformat())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La fecha debe ser futura.")
        self.assertEqual(Cita.objects.count(), 0)

    def test_hora_fuera_de_horario_rechazada(self):
        response = self._post(hora="20:00")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "9:00 a 19:00")
        self.assertEqual(Cita.objects.count(), 0)

    def test_domingo_rechazado(self):
        # Buscar el próximo domingo
        dias = (6 - date.today().weekday()) % 7 or 7
        domingo = date.today() + timedelta(days=dias)
        response = self._post(fecha=domingo.isoformat())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No se atiende los domingos.")
        self.assertEqual(Cita.objects.count(), 0)

    def test_doble_cita_rechazada(self):
        self._post()  # primera cita OK
        response = self._post()  # misma fecha/hora/vet
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ya existe")
        self.assertEqual(Cita.objects.count(), 1)