from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render

from core.decorators import role_required

from .forms import CitaForm

from django.http import HttpResponse

from datetime import date, timedelta
from core.models import Cita, Veterinario


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
    return render(request, "web/crear_cita.html", {"form": form})
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

    context = {
        "fecha": fecha,
        "dias_semana": dias_semana,
        "agenda_semana": agenda_semana,
        "citas_dia": citas_dia,
        "veterinarios": veterinarios,
        "filtro_vet": filtro_vet,
    }
    return render(request, "web/agenda.html", context)