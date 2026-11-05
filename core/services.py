from django.db import transaction
from core.models import Cita


@transaction.atomic
def cambiar_estado(cita, nuevo_estado):
    if not cita.puede_transicionar(nuevo_estado):
        raise ValueError(
            f"Transición inválida: {cita.estado} → {nuevo_estado}"
        )
    cita.estado = nuevo_estado
    cita.save(update_fields=["estado"])
    return cita