from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render

from .forms import CitaForm

@login_required
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