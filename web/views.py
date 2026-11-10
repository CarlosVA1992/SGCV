from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render

from core.decorators import role_required

from .forms import CitaForm

from django.http import HttpResponse

from datetime import date, time, timedelta
from core.models import Cita, Veterinario

from django.db.models import Q
from core.models import Mascota, Consulta, Adenda
from django.shortcuts import get_object_or_404
from .forms import ConsultaForm, AdendaForm
from core.optimizador import CitaPendiente, cargar_citas_pendientes, cargar_franjas_disponibles, optimizar



@role_required("administrador", "recepcionista")
def crear_cita(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    cita = form.save(commit=False)
                    cita._usuario_actual = request.user
                    cita.save()
            except IntegrityError:
                form.add_error(
                    None,
                    "Ya existe una cita para ese veterinario en esa fecha y hora.",
                )
            else:
                messages.success(request, "Cita registrada correctamente.")
                return redirect("crear_cita")
    else:
        form = CitaForm()
        # ... código anterior ...

    return render(request, "web/crear_cita.html", {
        "form": form,
        "mascotas_dict": getattr(form, 'mascotas_dict', {}) # Pasamos el diccionario
    })


@role_required("administrador", "veterinario")
def historial_dummy(request):
    """Vista temporal para probar el bloqueo por rol (se reemplaza en S2)."""
    return HttpResponse("Historial clínico (solo admin/veterinario)")

@login_required
def agenda(request):
    # Fecha seleccionada (por defecto hoy)
    fecha_str = request.GET.get("fecha")
    try:
        fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
    except ValueError:
        fecha = date.today()

    # Filtro por veterinario
    vet_id = request.GET.get("veterinario")
    veterinarios = Veterinario.objects.all()
    filtro_vet = None
    if vet_id:
        try:
            filtro_vet = Veterinario.objects.get(pk=vet_id)
        except Veterinario.DoesNotExist:
            filtro_vet = None

    # Semana: lunes a sábado de la semana de la fecha
    lunes = fecha - timedelta(days=fecha.weekday())
    dias_semana = [lunes + timedelta(days=i) for i in range(6)]  # lun–sáb

    # Citas de la semana
    qs = Cita.objects.filter(
        fecha__gte=dias_semana[0],
        fecha__lte=dias_semana[-1],
    ).select_related("mascota", "veterinario", "cliente")
    if filtro_vet:
        qs = qs.filter(veterinario=filtro_vet)

    # Agrupar por día
    agenda_semana = {dia: [] for dia in dias_semana}
    for cita in qs.order_by("hora"):
        if cita.fecha in agenda_semana:
            agenda_semana[cita.fecha].append(cita)

    # Vista de día
    citas_dia = [c for c in qs.filter(fecha=fecha).order_by("hora")]

    
    propuestas = {}
    citas_reprogramadas = [c for c in citas_dia if c.estado == "reprogramada"]
    
    if citas_reprogramadas:
        # 1. Cargar todas las franjas, pero filtrar SOLO las del día de hoy
        dia_semana = fecha.weekday() # 0=Lunes, 6=Domingo
        todas_franjas = cargar_franjas_disponibles()
        franjas_hoy = [f for f in todas_franjas if f.dia_semana == dia_semana]
        
        # 2. Cargar las citas que YA están ocupando un espacio hoy (para bloquearlas)
        citas_ocupadas = [
            {
                "veterinario_id": c.veterinario_id,
                "dia_semana": dia_semana,
                "hora_inicio": c.hora
            }
            for c in citas_dia if c.estado in ["programada", "en_atencion"]
        ]

        for c in citas_reprogramadas:
            citas_pendientes_dummy = [
                CitaPendiente(
                    id=c.id, duracion_min=c.duracion_min, prioridad=c.prioridad, 
                    cliente_id=c.cliente_id, mascota_id=c.mascota_id,veterinario_id=c.veterinario_id, motivo=c.motivo
                )
            ]
            
            # 3. Pasamos las citas_ocupadas al optimizador
            asignaciones = optimizar(
                citas_pendientes_dummy, 
                franjas_hoy, 
                citas_ocupadas=citas_ocupadas
            )
            
            if asignaciones:
                propuestas[c.id] = asignaciones[0].hora_inicio.strftime("%H:%M")
    context = {
            "fecha": fecha,
            "dias_semana": dias_semana,
            "agenda_semana": agenda_semana,
            "citas_dia": citas_dia,
            "veterinarios": veterinarios,
            "filtro_vet": filtro_vet,
            "propuestas": propuestas,
        }
    return render(request, "web/agenda.html", context)
    

@login_required

def buscar_mascota(request):
    q = request.GET.get("q", "").strip()
    resultados = []
    if q:
        resultados = Mascota.objects.filter(
            # Buscamos en código de mascota, nombre de mascota, 
            # nombre del cliente o teléfono del cliente
            Q(codigo__icontains=q) | 
            Q(nombre__icontains=q) | 
            Q(cliente__nombre__icontains=q) |
            Q(cliente__telefono__icontains=q)
        ).select_related("cliente").order_by("codigo")
        
    return render(request, "web/buscar_mascota.html", {
        "q": q,
        "resultados": resultados,
    })

@role_required("administrador", "veterinario")
def crear_consulta(request, mascota_id):
    mascota = get_object_or_404(Mascota, pk=mascota_id)
    if request.method == "POST":
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.mascota = mascota
            consulta.save()
            messages.success(request, "Consulta registrada correctamente.")
            return redirect("buscar_mascota")
    else:
        form = ConsultaForm()
    return render(request, "web/crear_consulta.html", {
        "form": form,
        "mascota": mascota,
    })

@role_required("administrador", "veterinario")
def crear_adenda(request, consulta_id):
    consulta = get_object_or_404(Consulta, pk=consulta_id)
    if request.method == "POST":
        form = AdendaForm(request.POST)
        if form.is_valid():
            adenda = form.save(commit=False)
            adenda.consulta = consulta
            adenda.usuario = request.user
            adenda.save()
            messages.success(request, "Adenda registrada correctamente. El registro original no ha sido modificado.")
            # Redirigimos a la evolución de la mascota de esa consulta
            return redirect("evolucion", mascota_id=consulta.mascota.id)
    else:
        form = AdendaForm(initial={"valor_anterior": consulta.diagnostico})
    return render(request, "web/crear_adenda.html", {
        "form": form,
        "consulta": consulta,
    })


@role_required("administrador", "veterinario")
def evolucion(request, mascota_id):
    mascota = get_object_or_404(Mascota, pk=mascota_id)
    consultas = Consulta.objects.filter(
        mascota=mascota
    ).select_related("veterinario").order_by("fecha", "id")

    ultima = consultas.last()  # la más reciente por fecha
    resumen = {
        "diagnostico_vigente": ultima.diagnostico if ultima else None,
        "fecha_ultima": ultima.fecha if ultima else None,
        "medicamentos_activos": mascota.medicamentos_activos,
        "alergias": mascota.alergias,
    }

    return render(request, "web/evolucion.html", {
        "mascota": mascota,
        "consultas": consultas,
        "resumen": resumen,
    })
from datetime import date

from core.services import optimizar_agenda


@role_required("administrador", "veterinario")
def propuesta_agenda(request):
    fecha_str = request.GET.get("fecha")
    try:
        fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
    except ValueError:
        fecha = date.today()

    propuesta = optimizar_agenda(fecha)
    return render(request, "web/propuesta_agenda.html", {
        "propuesta": propuesta,
        "fecha": fecha,
    })
from core.services import registrar_emergencia


@role_required("administrador", "veterinario")
def registrar_emergencia_view(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    resultado = None
    if request.method == "POST":
        try:
            minutos = int(request.POST.get("minutos_extra", 0))
        except ValueError:
            minutos = 0
        if minutos <= 0:
            messages.error(request, "Los minutos extra deben ser mayores que cero.")
        else:
            resultado = registrar_emergencia(cita.id, minutos, request.user)
            messages.success(request, "Emergencia registrada.")
    return render(request, "web/emergencia.html", {
        "cita": cita,
        "resultado": resultado,
    })

from .forms import ClienteForm

@role_required("administrador", "recepcionista")
def crear_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, "Cliente registrado. Ahora puede registrar su mascota.")
            return redirect("crear_mascota", cliente_id=cliente.id) # Lo mandamos directo a crear la mascota
    else:
        form = ClienteForm()
    return render(request, "web/crear_cliente.html", {"form": form})

from .forms import MascotaForm
from core.models import Cliente

@role_required("administrador", "recepcionista")
def crear_mascota(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == "POST":
        form = MascotaForm(request.POST)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.cliente = cliente
            mascota.save()
            messages.success(request, "Mascota registrada. Ya puede agendar una cita.")
            return redirect("crear_cita") # Lo mandamos directo a agendar cita
    else:
        form = MascotaForm()
    return render(request, "web/crear_mascota.html", {"form": form, "cliente": cliente})

from django.shortcuts import redirect

def redireccion_login(request):
    """Redirige al usuario según su rol después de iniciar sesión."""
    if request.user.groups.filter(name="veterinario").exists() and not request.user.is_superuser:
        return redirect("buscar_mascota")
    return redirect("agenda")
@role_required("administrador", "recepcionista")
def agregar_mascota(request, cliente_id):
    # Reutilizamos la lógica que ya teníamos para crear mascota
    return crear_mascota(request, cliente_id)

@role_required("administrador", "recepcionista")
def aplicar_reprogramacion(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    if request.method == "POST":
        nueva_hora_str = request.POST.get("nueva_hora")
        if nueva_hora_str:
            try:
                cita.hora = time.fromisoformat(nueva_hora_str)
                cita.estado = "programada" # Vuelve a estar activa
                cita.save()
                messages.success(request, f"Cita reprogramada exitosamente a las {nueva_hora_str}.")
            except IntegrityError:
                messages.error(request, f"No se pudo reprogramar: Ya existe otra cita para este veterinario a las {nueva_hora_str}.")
    
    return redirect("agenda")