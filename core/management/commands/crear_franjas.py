from datetime import time

from django.core.management.base import BaseCommand

from core.models import FranjaHoraria, Veterinario


class Command(BaseCommand):
    help = "Crea franjas horarias por defecto (lun–sáb, 9:00–19:00, bloques de 30 min)"

    def handle(self, *args, **options):
        creadas = 0
        for vet in Veterinario.objects.all():
            for dia in range(6):  # 0=lunes ... 5=sábado
                hora = 9
                minuto = 0
                while hora < 19:
                    h_inicio = time(hora, minuto)
                    minuto += 30
                    if minuto == 60:
                        minuto = 0
                        hora += 1
                    h_fin = time(hora, minuto)
                    _, creada = FranjaHoraria.objects.get_or_create(
                        veterinario=vet, dia_semana=dia, hora_inicio=h_inicio,
                        defaults={"hora_fin": h_fin, "disponible": True},
                    )
                    if creada:
                        creadas += 1
        self.stdout.write(f"Franjas creadas: {creadas}")