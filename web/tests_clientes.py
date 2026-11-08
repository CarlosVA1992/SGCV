from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Cliente, Mascota


class RegistroClientesTests(TestCase):
    def setUp(self):
        g_rec, _ = Group.objects.get_or_create(name="recepcionista")
        g_vet, _ = Group.objects.get_or_create(name="veterinario")
        
        self.user_rec = User.objects.create_user(username="rec", password="clave123")
        self.user_rec.groups.add(g_rec)
        self.user_vet = User.objects.create_user(username="vet", password="clave123")
        self.user_vet.groups.add(g_vet)

    def test_recepcionista_crea_cliente(self):
        self.client.login(username="rec", password="clave123")
        response = self.client.post(reverse("crear_cliente"), {
            "nombre": "María Gómez",
            "telefono": "70012345",
            "email": "maria@test.com"
        })
        self.assertEqual(response.status_code, 302) # Redirige a crear mascota
        self.assertEqual(Cliente.objects.count(), 1)
        cliente = Cliente.objects.first()
        self.assertEqual(cliente.nombre, "María Gómez")
        # Verifica que redirige a la URL correcta de mascota
        self.assertIn(f"/clientes/{cliente.id}/mascota/nueva/", response.url)

    def test_veterinario_no_crea_cliente(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(reverse("crear_cliente"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Cliente.objects.count(), 0)

    def test_recepcionista_crea_mascota(self):
        self.client.login(username="rec", password="clave123")
        cliente = Cliente.objects.create(nombre="Juan", telefono="123")
        
        response = self.client.post(reverse("crear_mascota", args=[cliente.id]), {
            "nombre": "Rocky",
            "especie": "Perro",
            "alergias": "Ninguna",
            "medicamentos_activos": "Ninguno"
        })
        self.assertEqual(response.status_code, 302) # Redirige a crear cita
        self.assertEqual(Mascota.objects.count(), 1)
        mascota = Mascota.objects.first()
        self.assertEqual(mascota.nombre, "Rocky")
        self.assertEqual(mascota.cliente, cliente)
        # Verifica que el código se autogeneró
        self.assertTrue(mascota.codigo.startswith("M-"))

    def test_campos_obligatorios_cliente(self):
        self.client.login(username="rec", password="clave123")
        response = self.client.post(reverse("crear_cliente"), {
            "nombre": "", # Vacío
            "telefono": "", # Vacío
        })
        self.assertEqual(response.status_code, 200) # Se queda en la página
        self.assertEqual(Cliente.objects.count(), 0)