from django.db import models
from django.db.models import Q


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=30)
    email = models.EmailField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["nombre"])]

    def __str__(self):
        return self.nombre


class Mascota(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="mascotas"
    )
    alergias = models.TextField(blank=True, default="")
    medicamentos_activos = models.TextField(blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["nombre"])]

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Mascota.objects.order_by("-id").first()
            numero = (ultimo.id + 1) if ultimo else 1
            self.codigo = f"M-{numero:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} — {self.nombre}"


class Veterinario(models.Model):
    nombre = models.CharField(max_length=150)
    usuario = models.OneToOneField(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.nombre


class Cita(models.Model):
    ESTADOS = [
        ("programada", "Programada"),
        ("en_atencion", "En atención"),
        ("reprogramada", "Reprogramada"),
        ("cancelada", "Cancelada"),
        ("inasistencia", "Inasistencia"),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50)
    duracion_min = models.PositiveIntegerField(default=30)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="programada")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["veterinario", "fecha", "hora"],
                condition=Q(estado__in=["programada", "en_atencion"]),
                name="unique_cita_vet_fecha_hora",
            )
        ]
        indexes = [
            models.Index(fields=["fecha"]),
            models.Index(fields=["veterinario"]),
        ]

    def puede_transicionar(self, nuevo_estado):
        return nuevo_estado in TRANSICIONES.get(self.estado, [])
    def __str__(self):
        return f"{self.fecha} {self.hora} — {self.mascota}"

TRANSICIONES = {
    "programada": ["en_atencion", "reprogramada", "cancelada", "inasistencia"],
    "en_atencion": [],
    "reprogramada": [],
    "cancelada": [],
    "inasistencia": [],
}
class Auditoria(models.Model):
    usuario = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    accion = models.CharField(max_length=100)
    registro_afectado = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-fecha", "-hora"]

    def __str__(self):
        return f"{self.fecha} {self.hora} — {self.accion}"

class Consulta(models.Model):
    mascota = models.ForeignKey(
        Mascota, on_delete=models.CASCADE, related_name="consultas"
    )
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT)
    fecha = models.DateField(auto_now_add=True)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2)
    diagnostico = models.TextField()
    tratamiento = models.TextField()

    class Meta:
        ordering = ["-fecha", "-id"]
        indexes = [models.Index(fields=["fecha"])]

    def __str__(self):
        return f"{self.fecha} — {self.mascota.nombre}"
class Adenda(models.Model):
    consulta = models.ForeignKey(
        Consulta, on_delete=models.PROTECT, related_name="adendas"
    )
    usuario = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True
    )
    valor_anterior = models.TextField()
    valor_nuevo = models.TextField()
    motivo = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-hora"]

    def __str__(self):
        return f"Adenda {self.fecha} — consulta {self.consulta_id}"

class FranjaHoraria(models.Model):
    DIAS = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
    ]

    veterinario = models.ForeignKey(
        Veterinario, on_delete=models.CASCADE, related_name="franjas"
    )
    dia_semana = models.PositiveSmallIntegerField(choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disponible = models.BooleanField(default=True)

    class Meta:
        ordering = ["veterinario", "dia_semana", "hora_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["veterinario", "dia_semana", "hora_inicio"],
                name="unique_franja_vet_dia_inicio",
            )
        ]

    def __str__(self):
        return f"{self.veterinario.nombre} — {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"