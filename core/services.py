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
from datetime import date

from core.optimizador import (
    cargar_citas_pendientes,
    cargar_franjas_disponibles,
    optimizar,
)


def optimizar_agenda(fecha: date) -> dict:
    """
    Propone una asignación automática de las citas del día a franjas disponibles.

    Devuelve un dict con:
      - asignaciones: lista de Asignacion
      - no_asignadas: lista de ids de citas que no cupieron
      - total_citas: número de citas evaluadas
    """
    citas = cargar_citas_pendientes(fecha)
    franjas = cargar_franjas_disponibles()
    asignaciones = optimizar(citas, franjas)

    asignadas_ids = {a.cita_id for a in asignaciones}
    no_asignadas = [c.id for c in citas if c.id not in asignadas_ids]

    return {
        "fecha": fecha,
        "total_citas": len(citas),
        "asignaciones": asignaciones,
        "no_asignadas": no_asignadas,
    }