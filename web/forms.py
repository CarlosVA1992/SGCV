from datetime import date, datetime

from django import forms
from core.models import Cita, Consulta, Adenda, Mascota




class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = [
            "cliente", "mascota", "veterinario",
            "fecha", "hora", "motivo", "tipo", "duracion_min", "prioridad",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha < date.today():
            raise forms.ValidationError("La fecha debe ser futura.")
        return fecha

    def clean_hora(self):
        hora = self.cleaned_data["hora"]
        # lunes=0 ... sábado=5, domingo=6
        dia = self.data.get("fecha")
        if dia:
            try:
                dia_semana = datetime.strptime(dia, "%Y-%m-%d").weekday()
            except ValueError:
                dia_semana = None
            if dia_semana == 6:
                raise forms.ValidationError("No se atiende los domingos.")
        if hora.hour < 9 or hora.hour >= 19:
            raise forms.ValidationError(
                "El horario de atención es de 9:00 a 19:00."
            )
        return hora

    def clean(self):
        cleaned = super().clean()
        cliente = cleaned.get("cliente")
        mascota = cleaned.get("mascota")
        if cliente and mascota and mascota.cliente_id != cliente.id:
            self.add_error(
                "mascota",
                "La mascota no pertenece al cliente seleccionado.",
            )
        return cleaned
    



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Creamos un diccionario con las mascotas y sus dueños
        # Esto lo inyectaremos en el HTML mediante un atributo data
        mascotas_dict = {str(m.id): m.cliente_id for m in Mascota.objects.all()}
        
        # Agregamos un atributo 'data-cliente' a cada opción del select de mascotas
        choices = [('', '---------')] + [
            (m.id, str(m)) for m in Mascota.objects.all()
        ]
        self.fields['mascota'].choices = choices
        
        # Guardamos el diccionario para usarlo en el template
        self.mascotas_dict = mascotas_dict


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ["veterinario", "peso_kg", "diagnostico", "tratamiento"]

    def clean_peso_kg(self):
        peso = self.cleaned_data["peso_kg"]
        if peso <= 0:
            raise forms.ValidationError("El peso debe ser mayor que cero.")
        return peso

    def clean_diagnostico(self):
        diagnostico = self.cleaned_data["diagnostico"].strip()
        if not diagnostico:
            raise forms.ValidationError("El diagnóstico es obligatorio.")
        return diagnostico

    def clean_tratamiento(self):
        tratamiento = self.cleaned_data["tratamiento"].strip()
        if not tratamiento:
            raise forms.ValidationError("El tratamiento es obligatorio.")
        return tratamiento

class AdendaForm(forms.ModelForm):
    class Meta:
        model = Adenda
        fields = ["valor_anterior", "valor_nuevo", "motivo"]

    def clean_motivo(self):
        motivo = self.cleaned_data["motivo"].strip()
        if not motivo:
            raise forms.ValidationError("El motivo de la adenda es obligatorio.")
        return motivo

from core.models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "telefono", "email"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. María Gómez"}),
            "telefono": forms.TextInput(attrs={"placeholder": "Ej. 70012345"}),
            "email": forms.EmailInput(attrs={"placeholder": "opcional@correo.com"}),
        }
from core.models import Mascota

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ["nombre", "especie", "alergias", "medicamentos_activos"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej. Rocky"}),
            "especie": forms.TextInput(attrs={"placeholder": "Ej. Perro, Gato"}),
        }