from django.contrib import admin
from .models import Cliente, Mascota, Veterinario, Cita

admin.site.register(Cliente)
admin.site.register(Mascota)
admin.site.register(Veterinario)
admin.site.register(Cita)