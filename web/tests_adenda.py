from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Adenda, Cliente, Consulta, Mascota, Veterinario


class AdendaTests(TestCase):
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
        self.consulta = Consulta.objects.create(
            mascota=self.mascota, veterinario=self.vet,
            peso_kg="12.50", diagnostico="Sano", tratamiento="Ninguno",
        )

    def _post_adenda(self, **overrides):
        data = {
            "valor_anterior": "Sano",
            "valor_nuevo": "Sano con observación",
            "motivo": "Corrección de diagnóstico",
        }
        data.update(overrides)
        return self.client.post(
            reverse("crear_adenda", args=[self.consulta.id]), data
        )

    def test_adenda_guarda_valores(self):
        self.client.login(username="vet", password="clave123")
        response = self._post_adenda()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Adenda.objects.count(), 1)
        adenda = Adenda.objects.first()
        self.assertEqual(adenda.valor_anterior, "Sano")
        self.assertEqual(adenda.valor_nuevo, "Sano con observación")
        self.assertEqual(adenda.motivo, "Corrección de diagnóstico")
        self.assertEqual(adenda.consulta, self.consulta)
        self.assertEqual(adenda.usuario, self.user_vet)

    def test_adenda_no_modifica_consulta_original(self):
        self.client.login(username="vet", password="clave123")
        self._post_adenda()
        self.consulta.refresh_from_db()
        self.assertEqual(self.consulta.diagnostico, "Sano")
        self.assertEqual(self.consulta.tratamiento, "Ninguno")

    def test_motivo_obligatorio(self):
        self.client.login(username="vet", password="clave123")
        response = self._post_adenda(motivo="   ")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo es obligatorio")
        self.assertEqual(Adenda.objects.count(), 0)

    def test_recepcionista_no_accede_a_adenda(self):
        self.client.login(username="rec", password="clave123")
        response = self.client.get(
            reverse("crear_adenda", args=[self.consulta.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_formulario_precarga_valor_anterior(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("crear_adenda", args=[self.consulta.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sano")