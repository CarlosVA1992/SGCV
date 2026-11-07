from datetime import date, time

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from core.models import Cliente, FranjaHoraria, Mascota, Veterinario
from core.optimizador import (
    CitaPendiente,
    FranjaDisponible,
    optimizar,
)


class OptimizadorTests(TestCase):
    """Tests unitarios de la función optimizar() sin tocar la BD."""

    def _cita(self, id, dur=30, prioridad=2):
        return CitaPendiente(
            id=id, duracion_min=dur, prioridad=prioridad,
            cliente_id=1, mascota_id=1, motivo="test",
        )

    def _franja(self, vet=1, dia=0, ini=(9, 0), fin=(9, 30)):
        return FranjaDisponible(
            veterinario_id=vet, dia_semana=dia,
            hora_inicio=time(*ini), hora_fin=time(*fin),
        )

    def test_asigna_cita_a_franja_compatible(self):
        citas = [self._cita(1)]
        franjas = [self._franja()]
        asignaciones = optimizar(citas, franjas)
        self.assertEqual(len(asignaciones), 1)
        self.assertEqual(asignaciones[0].cita_id, 1)
        self.assertEqual(asignaciones[0].veterinario_id, 1)

    def test_no_solapamiento_dos_citas_misma_franja(self):
        citas = [self._cita(1), self._cita(2)]
        franjas = [self._franja()]
        asignaciones = optimizar(citas, franjas)
        # Solo una puede ocupar la única franja
        self.assertEqual(len(asignaciones), 1)

    def test_duracion_incompatible_no_asigna(self):
        citas = [self._cita(1, dur=60)]  # 60 min
        franjas = [self._franja(ini=(9, 0), fin=(9, 30))]  # 30 min
        asignaciones = optimizar(citas, franjas)
        self.assertEqual(len(asignaciones), 0)

    def test_dos_citas_dos_franjas(self):
        citas = [self._cita(1), self._cita(2)]
        franjas = [
            self._franja(ini=(9, 0), fin=(9, 30)),
            self._franja(ini=(9, 30), fin=(10, 0)),
        ]
        asignaciones = optimizar(citas, franjas)
        self.assertEqual(len(asignaciones), 2)
        citas_asignadas = {a.cita_id for a in asignaciones}
        self.assertEqual(citas_asignadas, {1, 2})

    def test_prefiere_horario_temprano(self):
        # Con dos franjas, la función objetivo prefiere la más temprana
        citas = [self._cita(1)]
        franjas = [
            self._franja(ini=(9, 0), fin=(9, 30)),
            self._franja(ini=(15, 0), fin=(15, 30)),
        ]
        asignaciones = optimizar(citas, franjas)
        self.assertEqual(len(asignaciones), 1)
        self.assertEqual(asignaciones[0].hora_inicio, time(9, 0))

    def test_sin_citas_devuelve_vacio(self):
        self.assertEqual(optimizar([], [self._franja()]), [])

    def test_sin_franjas_devuelve_vacio(self):
        self.assertEqual(optimizar([self._cita(1)], []), [])


class PropuestaAgendaViewTests(TestCase):
    """Tests de la vista /agenda/propuesta/."""

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

        FranjaHoraria.objects.create(
            veterinario=self.vet, dia_semana=0,
            hora_inicio=time(9, 0), hora_fin=time(9, 30),
        )

    def test_veterinario_accede_a_propuesta(self):
        self.client.login(username="vet", password="clave123")
        response = self.client.get(reverse("propuesta_agenda"))
        self.assertEqual(response.status_code, 200)

    def test_recepcionista_no_accede_a_propuesta(self):
        self.client.login(username="rec", password="clave123")
        response = self.client.get(reverse("propuesta_agenda"))
        self.assertEqual(response.status_code, 403)