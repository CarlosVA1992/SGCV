from django.db import transaction
from core.models import Cita


from core.models import Auditoria

@transaction.atomic
def cambiar_estado(cita, nuevo_estado, usuario=None):
    if not cita.puede_transicionar(nuevo_estado):
        raise ValueError(
            f"Transición inválida: {cita.estado} → {nuevo_estado}"
        )
    estado_anterior = cita.estado
    cita.estado = nuevo_estado
    cita.save(update_fields=["estado"])
    Auditoria.objects.create(
        usuario=usuario,
        accion=f"cita_{nuevo_estado}",
        registro_afectado=f"cita:{cita.id} (de {estado_anterior} a {nuevo_estado})",
    )
    return cita