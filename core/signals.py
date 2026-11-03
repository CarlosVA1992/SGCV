from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Auditoria, Cita


@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):
    Auditoria.objects.create(
        usuario=user,
        accion="login",
        registro_afectado=f"user:{user.id}",
    )


@receiver(post_save, sender=Cita)
def registrar_cita(sender, instance, created, **kwargs):
    accion = "cita_creada" if created else "cita_modificada"
    Auditoria.objects.create(
        usuario=getattr(instance, "_usuario_actual", None),
        accion=accion,
        registro_afectado=f"cita:{instance.id}",
    )