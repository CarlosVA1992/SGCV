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

from datetime import timedelta

from core.models import Cita


def registrar_emergencia(cita_id: int, minutos_extra: int, usuario=None) -> dict:
    """
    Extiende una cita por minutos_extra y devuelve las citas afectadas
    (las que empiezan después de la cita extendida el mismo día).
    No modifica el estado de las citas; solo calcula el impacto.
    """
    from core.models import Auditoria

    cita = Cita.objects.select_related("veterinario", "cliente").get(pk=cita_id)
    nueva_duracion = cita.duracion_min + minutos_extra
    hora_fin_original = _sumar_minutos(cita.hora, cita.duracion_min)
    hora_fin_nueva = _sumar_minutos(cita.hora, nueva_duracion)

    # Citas del mismo veterinario y día que empiezan después de la original
    afectadas = Cita.objects.filter(
        veterinario=cita.veterinario,
        fecha=cita.fecha,
        hora__gte=hora_fin_original,
        estado__in=["programada", "reprogramada"],
    ).exclude(pk=cita.pk).select_related("cliente", "mascota")

    # Actualizar duración de la cita extendida
    cita.duracion_min = nueva_duracion
    cita.save(update_fields=["duracion_min"])

    Auditoria.objects.create(
        usuario=usuario,
        accion="emergencia_registrada",
        registro_afectado=f"cita:{cita.id} (+{minutos_extra} min)",
    )

    return {
        "cita": cita,
        "minutos_extra": minutos_extra,
        "hora_fin_original": hora_fin_original,
        "hora_fin_nueva": hora_fin_nueva,
        "afectadas": list(afectadas),
    }


def _sumar_minutos(hora, minutos):
    from datetime import time
    total = hora.hour * 60 + hora.minute + minutos
    return time(total // 60, total % 60)