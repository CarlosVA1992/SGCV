from django.contrib import admin
from .models import Cliente, Mascota, Veterinario, Cita, Auditoria

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "mascota", "veterinario", "estado")

admin.site.register(Cliente)
admin.site.register(Mascota)
admin.site.register(Veterinario)
admin.site.register(Auditoria)