from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Cliente, Consulta, Mascota, Veterinario


class EvolucionTests(TestCase):
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
            nombre="Firulais", especie="Perro", cliente=self.cliente,
            alergias="Penicilina", medicamentos_activos="Antipulgas",
        )
        self.vet = Veterinario.objects.create(nombre="Dra. Vargas")

        hoy = date.today()
        self.c1 = Consulta.objects.create(
            mascota=self.mascota, veterinario=self.vet,
            peso_kg="10.00", diagnostico="Primera consulta",
            tratamiento="Reposo",
        )
        self.c2 = Consulta.objects.create(
            mascota=self.mascota, veterinario=self.vet,
            peso_kg="12.50", diagnostico="Mejoría",
            tratamiento="Continuar",
        )
        # Forzar fechas distintas para verificar orden
        Consulta.objects.filter(pk=self.c1.pk).update(fecha=hoy - timedelta(days=10))
        Consulta.objects.filter(pk=self.c2.pk).update(fecha=hoy)

    def test_orden_cronologico_ascendente(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("evolucion", args=[self.mascota.id])
        )
        self.assertEqual(response.status_code, 200)
        consultas = list(response.context["consultas"])
        self.assertEqual(consultas[0].id, self.c1.id)  # más antigua primero
        self.assertEqual(consultas[1].id, self.c2.id)

    def test_resumen_muestra_ultimo_diagnostico(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("evolucion", args=[self.mascota.id])
        )
        resumen = response.context["resumen"]
        self.assertEqual(resumen["diagnostico_vigente"], "Mejoría")

    def test_resumen_muestra_alergias_y_medicamentos(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("evolucion", args=[self.mascota.id])
        )
        self.assertContains(response, "Penicilina")
        self.assertContains(response, "Antipulgas")

    def test_mascota_sin_consultas_muestra_mensaje(self):
        mascota_vacia = Mascota.objects.create(
            nombre="SinHistorial", especie="Gato", cliente=self.cliente
        )
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("evolucion", args=[mascota_vacia.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sin consultas registradas")
        self.assertEqual(response.context["resumen"]["diagnostico_vigente"], None)

    def test_recepcionista_no_accede_a_evolucion(self):
        self.client.login(username="rec", password="clave123")
        response = self.client.get(
            reverse("evolucion", args=[self.mascota.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_veterinario_accede_a_evolucion(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(
            reverse("evolucion", args=[self.mascota.id])
        )
        self.assertEqual(response.status_code, 200)