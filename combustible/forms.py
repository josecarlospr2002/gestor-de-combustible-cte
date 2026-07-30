from django import forms
from .models import SolicitudCombustible, Transporte, DetalleSolicitud


class SolicitudCombustibleForm(forms.ModelForm):
    class Meta:
        model = SolicitudCombustible
        fields = ['motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describa el motivo de la solicitud',
                'rows': '3'
            }),
        }
        labels = {
            'motivo': 'Motivo de la Solicitud',
        }

class TransporteForm(forms.ModelForm):
    class Meta:
        model = Transporte
        fields = ['tipo_combustible', 'empresa', 'tipo_vehiculo', 'chapa']
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
        }
        labels = {
            'tipo_combustible': 'Tipo de Combustible',
            'empresa': 'Empresa',
            'tipo_vehiculo': 'Tipo de Vehículo',
            'chapa': 'Chapa',
        }
        error_messages = {
            'tipo_combustible': {'required': 'Rellene todos los campos, por favor.'},
            'empresa': {'required': 'Rellene todos los campos, por favor.'},
            'tipo_vehiculo': {'required': 'Rellene todos los campos, por favor.'},
            'chapa': {'required': 'Rellene todos los campos, por favor.'},
        }

class DetalleSolicitudForm(forms.ModelForm):
    class Meta:
        model = DetalleSolicitud
        fields = ['actividad', 'via_blanca', 'cte', 'ic']
        widgets = {
            'actividad': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Actividad'
            }),
            'via_blanca': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'cte': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'ic': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'actividad': '',
            'via_blanca': '',
            'cte': '',
            'ic': '',
        }