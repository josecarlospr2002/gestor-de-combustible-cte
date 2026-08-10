from django import forms
from .models import SolicitudCombustible, Transporte, DetalleSolicitud, SuministroCombustible


class SolicitudCombustibleForm(forms.ModelForm):
    class Meta:
        model = SolicitudCombustible
        fields = ['nombre', 'fecha_hora', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional: nombre de la solicitud'
            }),
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional: descripción de la solicitud',
                'rows': '2'
            }),
        }
        labels = {
            'nombre': 'Nombre de la Solicitud',
            'fecha_hora': 'Fecha y Hora',
            'descripcion': 'Descripción',
        }


class TransporteForm(forms.ModelForm):
    class Meta:
        model = Transporte
        fields = ['tipo_combustible', 'empresa', 'tipo_vehiculo', 'chapa', 'ic']
        widgets = {
            'tipo_combustible': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el tipo de combustible'
            }),
            'empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la empresa'
            }),
            'tipo_vehiculo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el tipo de vehículo'
            }),
            'chapa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la chapa'
            }),
            'ic': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'tipo_combustible': 'Tipo de Combustible',
            'empresa': 'Empresa',
            'tipo_vehiculo': 'Tipo de Vehículo',
            'chapa': 'Chapa',
            'ic': 'I/C',
        }
        error_messages = {
            'tipo_combustible': {'required': 'Rellene todos los campos, por favor.'},
            'empresa': {'required': 'Rellene todos los campos, por favor.'},
            'tipo_vehiculo': {'required': 'Rellene todos los campos, por favor.'},
            'chapa': {'required': 'Rellene todos los campos, por favor.'},
            'ic': {'required': 'Rellene todos los campos, por favor.'},
        }


class DetalleSolicitudForm(forms.ModelForm):
    class Meta:
        model = DetalleSolicitud
        fields = ['actividad', 'cant_abastecer']
        widgets = {
            'actividad': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Actividad'
            }),
            'cant_abastecer': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
        }


class SuministroCombustibleForm(forms.ModelForm):
    class Meta:
        model = SuministroCombustible
        fields = ['nombre', 'fecha_hora', 'tipo_combustible', 'cantidad', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional: nombre del suministro'
            }),
            'fecha_hora': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'tipo_combustible': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Gasolina, Diésel, Petróleo...'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional: nota, recuerdo u observación',
                'rows': '3'
            }),
        }
        labels = {
            'nombre': 'Nombre del Suministro',
            'fecha_hora': 'Fecha y Hora',
            'tipo_combustible': 'Tipo de Combustible',
            'cantidad': 'Cantidad de Combustible',
            'descripcion': 'Descripción / Nota',
        }
        error_messages = {
            'tipo_combustible': {'required': 'El tipo de combustible es obligatorio.'},
            'cantidad': {'required': 'La cantidad es obligatoria.'},
        }