from django import forms
from .models import SolicitudCombustible, Transporte


class SolicitudCombustibleForm(forms.ModelForm):
    class Meta:
        model = SolicitudCombustible
        fields = ['cantidad_litros', 'motivo']
        widgets = {
            'cantidad_litros': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la cantidad en litros',
                'min': '1',
                'step': '0.01'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describa el motivo de la solicitud',
                'rows': '4'
            }),
        }
        labels = {
            'cantidad_litros': 'Cantidad de Combustible (Litros)',
            'motivo': 'Motivo de la Solicitud',
        }


class TransporteForm(forms.ModelForm):
    class Meta:
        model = Transporte
        fields = '__all__'
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
            'actividad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la actividad'
            }),
        }
        labels = {
            'tipo_combustible': 'Tipo de Combustible',
            'empresa': 'Empresa',
            'tipo_vehiculo': 'Tipo de Vehículo',
            'chapa': 'Chapa',
            'actividad': 'Actividad',
        }
        error_messages = {
            'tipo_combustible': {'required': 'Rellene todos los campos, por favor.'},
            'empresa': {'required': 'Rellene todos los campos, por favor.'},
            'tipo_vehiculo': {'required': 'Rellene todos los campos, por favor.'},
            'chapa': {'required': 'Rellene todos los campos, por favor.'},
            'actividad': {'required': 'Rellene todos los campos, por favor.'},
        }