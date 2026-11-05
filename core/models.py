from django.db import models


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