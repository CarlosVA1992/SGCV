from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Cliente, Consulta, Mascota, Veterinario


class ConsultaTests(TestCase):
    def setUp(self):
        # Grupos
        self.g_admin, _ = Group.objects.get_or_create(name="administrador")
        self.g_vet, _ = Group.objects.get_or_create(name="veterinario")
        self.g_rec, _ = Group.objects.get_or_create(name="recepcionista")

        # Usuarios
        self.user_vet = User.objects.create_user(
            username="vet", password="clave123"
        )
        self.user_vet.groups.add(self.g_vet)
        self.user_rec = User.objects.create_user(
            username="rec", password="clave123"
        )
        self.user_rec.groups.add(self.g_rec)

        # Datos
        self.cliente = Cliente.objects.create(nombre="Ana", telefono="70000000")
        self.mascota = Mascota.objects.create(
            nombre="Firulais", especie="Perro", cliente=self.cliente
        )
        self.vet = Veterinario.objects.create(nombre="Dra. Vargas")

    # --- Búsqueda de mascota ---

    def test_busqueda_por_codigo(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("buscar_mascota"), {"q": self.mascota.codigo}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Firulais")

    def test_busqueda_por_nombre(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("buscar_mascota"), {"q": "Firu"}
        )
        self.assertContains(response, "Firulais")

    def test_busqueda_sin_resultados(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("buscar_mascota"), {"q": "xyz"}
        )
        self.assertContains(response, "No se encontraron mascotas.")

    # --- Validaciones de consulta ---

    def _post_consulta(self, **overrides):
        data = {
            "veterinario": self.vet.id,
            "peso_kg": "12.50",
            "diagnostico": "Sano",
            "tratamiento": "Ninguno",
        }
        data.update(overrides)
        return self.client.post(
            reverse("crear_consulta", args=[self.mascota.id]), data
        )

    def test_consulta_valida_se_crea(self):
        self.client.login(username="vet", password="clave123")
        response = self._post_consulta()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Consulta.objects.count(), 1)

    def test_peso_cero_rechazado(self):
        self.client.login(username="vet", password="clave123")
        response = self._post_consulta(peso_kg="0")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mayor que cero")
        self.assertEqual(Consulta.objects.count(), 0)

    def test_diagnostico_vacio_rechazado(self):
        self.client.login(username="vet", password="clave123")
        response = self._post_consulta(diagnostico="")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo es obligatorio")
        self.assertEqual(Consulta.objects.count(), 0)

    # --- Bloqueo por rol ---

    def test_recepcionista_no_accede_a_consulta(self):
        self.client.login(username="rec", password="clave123")
        response = self.client.get(
            reverse("crear_consulta", args=[self.mascota.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_veterinario_accede_a_consulta(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("crear_consulta", args=[self.mascota.id])
        )
        self.assertEqual(response.status_code, 200)