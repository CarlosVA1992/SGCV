"""
Estructuras de datos para el optimizador de asignación (REQ-07).

No implementa el algoritmo todavía; solo define cómo se representan
las citas pendientes y las franjas disponibles.
"""

from dataclasses import dataclass, field
from datetime import date, time

from core.models import Cita, FranjaHoraria, Veterinario


@dataclass
class CitaPendiente:
    """Representa una cita que el optimizador debe asignar."""
    id: int
    duracion_min: int
    prioridad: int  # 1=baja ... 4=urgente
    cliente_id: int
    mascota_id: int
    motivo: str


@dataclass
class FranjaDisponible:
    """Representa un bloque de tiempo asignable de un veterinario."""
    veterinario_id: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time


@dataclass
class Asignacion:
    """Resultado del optimizador: cita asignada a un veterinario y franja."""
    cita_id: int
    veterinario_id: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time


def cargar_citas_pendientes(fecha: date) -> list[CitaPendiente]:
    """Citas del día que aún no tienen estado final."""
    qs = Cita.objects.filter(
        fecha=fecha,
        estado__in=["programada", "reprogramada"],
    ).select_related("cliente", "mascota")
    return [
        CitaPendiente(
            id=c.id,
            duracion_min=c.duracion_min,
            prioridad=c.prioridad,
            cliente_id=c.cliente_id,
            mascota_id=c.mascota_id,
            motivo=c.motivo,
        )
        for c in qs
    ]


def cargar_franjas_disponibles() -> list[FranjaDisponible]:
    """Franjas de todos los veterinarios marcadas como disponibles."""
    qs = FranjaHoraria.objects.filter(
        disponible=True
    ).select_related("veterinario")
    return [
        FranjaDisponible(
            veterinario_id=f.veterinario_id,
            dia_semana=f.dia_semana,
            hora_inicio=f.hora_inicio,
            hora_fin=f.hora_fin,
        )
        for f in qs
    ]