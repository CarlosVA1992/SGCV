from django.contrib import admin
from .models import Cliente, Mascota, Veterinario, Cita, Auditoria

admin.site.register(Cliente)
admin.site.register(Mascota)
admin.site.register(Veterinario)
admin.site.register(Cita)
admin.site.register(Auditoria)