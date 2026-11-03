from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class RoleAccessTests(TestCase):
    def setUp(self):
        # Crear grupos
        self.grupo_admin, _ = Group.objects.get_or_create(name="administrador")
        self.grupo_vet, _ = Group.objects.get_or_create(name="veterinario")
        self.grupo_rec, _ = Group.objects.get_or_create(name="recepcionista")

        # Usuario recepcionista
        self.user_rec = User.objects.create_user(
            username="recepcion", password="clave123"
        )
        self.user_rec.groups.add(self.grupo_rec)

        # Usuario veterinario
        self.user_vet = User.objects.create_user(
            username="veterinario", password="clave123"
        )
        self.user_vet.groups.add(self.grupo_vet)

    def test_recepcionista_no_accede_a_historial(self):
        self.client.login(username="recepcion", password="clave123")
        response = self.client.get(reverse("historial_dummy"))
        self.assertEqual(response.status_code, 403)

    def test_veterinario_accede_a_historial(self):
        self.client.login(username="veterinario", password="clave123")
        response = self.client.get(reverse("historial_dummy"))
        self.assertEqual(response.status_code, 200)

    def test_veterinario_no_accede_a_crear_cita(self):
        self.client.login(username="veterinario", password="clave123")
        response = self.client.get(reverse("crear_cita"))
        self.assertEqual(response.status_code, 403)

    def test_recepcionista_accede_a_crear_cita(self):
        self.client.login(username="recepcion", password="clave123")
        response = self.client.get(reverse("crear_cita"))
        self.assertEqual(response.status_code, 200)

    def test_anonimo_redirige_a_login(self):
        response = self.client.get(reverse("historial_dummy"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
class PasswordHashTests(TestCase):
    def test_password_se_guarda_hasheada(self):
        user = User.objects.create_user(
            username="hash_test", password="clave123"
        )
        # La contraseña no se guarda en texto plano
        self.assertNotEqual(user.password, "clave123")
        # Django usa PBKDF2 por defecto
        self.assertTrue(user.password.startswith("pbkdf2_"))
        # El check nativo la valida correctamente
        self.assertTrue(user.check_password("clave123"))
        self.assertFalse(user.check_password("otra_clave"))

    def test_validadores_de_password_activos(self):
        from django.conf import settings
        self.assertTrue(len(settings.AUTH_PASSWORD_VALIDATORS) > 0)