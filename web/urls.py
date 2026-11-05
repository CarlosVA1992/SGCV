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
]