"""
Estructuras de datos y optimizador de asignación (REQ-07).
"""

from dataclasses import dataclass
from datetime import date, time

import pulp

from core.models import Cita, FranjaHoraria


@dataclass
class CitaPendiente:
    id: int
    duracion_min: int
    prioridad: int  # 1=baja ... 4=urgente
    cliente_id: int
    mascota_id: int
    motivo: str


@dataclass
class FranjaDisponible:
    veterinario_id: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time


@dataclass
class Asignacion:
    cita_id: int
    veterinario_id: int
    dia_semana: int
    hora_inicio: time
    hora_fin: time


def cargar_citas_pendientes(fecha: date) -> list[CitaPendiente]:
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


def optimizar(citas: list[CitaPendiente], franjas: list[FranjaDisponible],
              pesos: dict | None = None) -> list[Asignacion]:
    """
    Asigna citas a franjas minimizando huecos y espera ponderada por prioridad.
    Si una cita no cabe, se marca como no asignada con costo alto.
    """
    if pesos is None:
        pesos = {"huecos": 1.0, "espera": 2.0}

    if not citas or not franjas:
        return []

    # Pares viables por duración
    pares = []
    for c in citas:
        for f in franjas:
            if _minutos_entre(f.hora_inicio, f.hora_fin) >= c.duracion_min:
                pares.append((c, f))

    prob = pulp.LpProblem("asignacion_citas", pulp.LpMinimize)

    # Variable binaria por par viable
    x = {}
    for c, f in pares:
        clave = (c.id, f.veterinario_id, f.dia_semana, f.hora_inicio)
        x[clave] = pulp.LpVariable(
            f"x_{c.id}_{f.veterinario_id}_{f.dia_semana}_"
            f"{f.hora_inicio.hour}_{f.hora_inicio.minute}",
            lowBound=0, upBound=1, cat="Binary",
        )

    # Variable de cita no asignada (penalizada)
    no_asignada = {}
    for c in citas:
        no_asignada[c.id] = pulp.LpVariable(
            f"no_asignada_{c.id}", lowBound=0, upBound=1, cat="Binary"
        )

    # Cada cita: asignada a una franja O no asignada
    for c in citas:
        prob += (
            pulp.lpSum(
                x[(c.id, f.veterinario_id, f.dia_semana, f.hora_inicio)]
                for cc, f in pares if cc.id == c.id
            )
            + no_asignada[c.id]
            == 1
        )

    # Cada franja: a lo sumo una cita
    for f in franjas:
        prob += pulp.lpSum(
            x[(c.id, f.veterinario_id, f.dia_semana, f.hora_inicio)]
            for c, ff in pares
            if ff.veterinario_id == f.veterinario_id
            and ff.dia_semana == f.dia_semana
            and ff.hora_inicio == f.hora_inicio
        ) <= 1

    # Función objetivo
    COSTO_NO_ASIGNAR = 10000
    costo = []
    for c, f in pares:
        minuto_dia = f.hora_inicio.hour * 60 + f.hora_inicio.minute
        espera_pond = (5 - c.prioridad) * minuto_dia
        hueco = _minutos_entre(f.hora_inicio, f.hora_fin) - c.duracion_min
        costo.append(
            (pesos["huecos"] * hueco + pesos["espera"] * espera_pond)
            * x[(c.id, f.veterinario_id, f.dia_semana, f.hora_inicio)]
        )
    for c in citas:
        costo.append(COSTO_NO_ASIGNAR * no_asignada[c.id])
    prob += pulp.lpSum(costo)

    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    # Extraer asignaciones
    asignaciones = []
    for c, f in pares:
        var = x[(c.id, f.veterinario_id, f.dia_semana, f.hora_inicio)]
        if var.varValue and var.varValue > 0.5:
            fin = _sumar_minutos(f.hora_inicio, c.duracion_min)
            asignaciones.append(Asignacion(
                cita_id=c.id,
                veterinario_id=f.veterinario_id,
                dia_semana=f.dia_semana,
                hora_inicio=f.hora_inicio,
                hora_fin=fin,
            ))
    return asignaciones


def _minutos_entre(inicio, fin):
    return (fin.hour * 60 + fin.minute) - (inicio.hour * 60 + inicio.minute)


def _sumar_minutos(hora, minutos):
    total = hora.hour * 60 + hora.minute + minutos
    return time(total // 60, total % 60)