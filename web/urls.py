from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("citas/nueva/", views.crear_cita, name="crear_cita"),
    path("login/", auth_views.LoginView.as_view(
        template_name="web/login.html"
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("historial/", views.historial_dummy, name="historial_dummy"),
    path("agenda/", views.agenda, name="agenda"),
    path("mascotas/", views.buscar_mascota, name="buscar_mascota"),
    path("mascotas/<int:mascota_id>/consulta/", views.crear_consulta, name="crear_consulta"),
    path("consultas/<int:consulta_id>/adenda/", views.crear_adenda, name="crear_adenda"),
    path("mascotas/<int:mascota_id>/evolucion/", views.evolucion, name="evolucion"),
    path("agenda/propuesta/", views.propuesta_agenda, name="propuesta_agenda"),
    path("citas/<int:cita_id>/emergencia/", views.registrar_emergencia_view, name="emergencia"),
    path("backup/", views.ejecutar_backup, name="ejecutar_backup"),
]