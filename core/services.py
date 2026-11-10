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


from datetime import date
from core.models import Cita
from core.optimizador import cargar_franjas_disponibles, optimizar, CitaPendiente

def optimizar_agenda(fecha: date) -> dict:
    """
    Propone una asignación automática para las citas del día que NO están agendadas,
    respetando los horarios que ya están ocupados.
    """
    # 1. Obtener las citas reales de la BD para saber cuáles están ocupadas
    citas_reales = Cita.objects.filter(fecha=fecha).select_related("veterinario")
    
    # 2. Separar las citas que ya tienen hora (programadas) de las que necesitan hora (reprogramadas)
    citas_ya_agendadas = [c for c in citas_reales if c.estado in ["programada", "en_atencion"]]
    citas_por_agendar = [c for c in citas_reales if c.estado == "reprogramada"]
    
    # 3. Convertir las citas por agendar a la estructura que entiende el optimizador
    citas_pendientes = [
        CitaPendiente(
            id=c.id, duracion_min=c.duracion_min, prioridad=c.prioridad,
            cliente_id=c.cliente_id, mascota_id=c.mascota_id, 
            veterinario_id=c.veterinario_id, motivo=c.motivo
        ) for c in citas_por_agendar
    ]
    
    # 4. Filtrar franjas solo para el día de la semana actual
    dia_semana = fecha.weekday()
    todas_franjas = cargar_franjas_disponibles()
    franjas_hoy = [f for f in todas_franjas if f.dia_semana == dia_semana]
    
    # 5. Crear la lista de bloqueos (las que ya están en la agenda)
    citas_ocupadas = [
        {
            "veterinario_id": c.veterinario_id,
            "dia_semana": dia_semana,
            "hora_inicio": c.hora
        }
        for c in citas_ya_agendadas
    ]

    # 6. Ejecutar el optimizador SOLO con las citas pendientes
    asignaciones = optimizar(citas_pendientes, franjas_hoy, citas_ocupadas=citas_ocupadas)

    asignadas_ids = {a.cita_id for a in asignaciones}
    no_asignadas = [c.id for c in citas_por_agendar if c.id not in asignadas_ids]

    return {
        "fecha": fecha,
        "total_citas": len(citas_por_agendar),
        "asignaciones": asignaciones,
        "no_asignadas": no_asignadas,
    }

from datetime import timedelta

from core.models import Cita


def registrar_emergencia(cita_id: int, minutos_extra: int, usuario=None,
                         reprogramar: bool = True) -> dict:
    """
    Extiende una cita por minutos_extra y, opcionalmente, reprograma en lote
    las citas afectadas (las que empiezan después de la cita extendida).
    """
    from core.models import Auditoria
    from core.optimizador import (
        cargar_citas_pendientes,
        cargar_franjas_disponibles,
        optimizar,
    )

    cita = Cita.objects.select_related("veterinario", "cliente").get(pk=cita_id)
    nueva_duracion = cita.duracion_min + minutos_extra
    hora_fin_original = _sumar_minutos(cita.hora, cita.duracion_min)
    hora_fin_nueva = _sumar_minutos(cita.hora, nueva_duracion)

    afectadas = list(
        Cita.objects.filter(
            veterinario=cita.veterinario,
            fecha=cita.fecha,
            hora__gte=hora_fin_original,
            estado__in=["programada", "reprogramada"],
        ).exclude(pk=cita.pk).select_related("cliente", "mascota")
    )

    # Extender la cita original
    cita.duracion_min = nueva_duracion
    cita.save(update_fields=["duracion_min"])

    # Reprogramar en lote: cambiar estado y proponer nuevos horarios
    propuesta = []
    if reprogramar and afectadas:
        for c in afectadas:
            c.estado = "reprogramada"
            c.save(update_fields=["estado"])

        # Calcular propuesta de nuevos horarios con el optimizador
        citas_pend = cargar_citas_pendientes(cita.fecha)
        franjas = cargar_franjas_disponibles()
        propuesta = optimizar(citas_pend, franjas)

        Auditoria.objects.create(
            usuario=usuario,
            accion="citas_reprogramadas_lote",
            registro_afectado=f"{len(afectadas)} citas (emergencia cita:{cita.id})",
        )

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
        "afectadas": afectadas,
        "propuesta": propuesta,
        "reprogramadas": len(afectadas) if reprogramar else 0,
    }


def _sumar_minutos(hora, minutos):
    from datetime import time
    total = hora.hour * 60 + hora.minute + minutos
    return time(total // 60, total % 60)