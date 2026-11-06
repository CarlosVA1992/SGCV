from django.contrib import admin
from .models import Adenda, Cliente, Mascota, Veterinario, Cita, Auditoria, Consulta, FranjaHoraria

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "mascota", "veterinario", "estado", "prioridad")

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "mascota", "veterinario", "peso_kg")

@admin.register(Adenda)
class AdendaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "consulta", "usuario")
admin.site.register(Cliente)
@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "especie", "cliente")
admin.site.register(Veterinario)
admin.site.register(Auditoria)


@admin.register(FranjaHoraria)
class FranjaHorariaAdmin(admin.ModelAdmin):
    list_display = ("veterinario", "dia_semana", "hora_inicio", "hora_fin", "disponible")
    list_filter = ("veterinario", "dia_semana", "disponible")