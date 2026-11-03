from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

from core.decorators import role_required

from .forms import CitaForm

from django.http import HttpResponse


@role_required("administrador", "recepcionista")
def crear_cita(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cita registrada correctamente.")
                return redirect("crear_cita")
            except IntegrityError:
                form.add_error(
                    None,
                    "Ya existe una cita para ese veterinario en esa fecha y hora.",
                )
    else:
        form = CitaForm()
    return render(request, "web/crear_cita.html", {"form": form})

@role_required("administrador", "veterinario")
def historial_dummy(request):
    """Vista temporal para probar el bloqueo por rol (se reemplaza en S2)."""
    return HttpResponse("Historial clínico (solo admin/veterinario)")