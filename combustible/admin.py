from django.contrib import admin
from .models import SolicitudCombustible, Transporte, DetalleSolicitud


@admin.register(SolicitudCombustible)
class SolicitudCombustibleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'estado', 'fecha_hora')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('nombre', 'descripcion')


@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_display = ('chapa', 'tipo_vehiculo', 'tipo_combustible', 'empresa', 'ic')
    list_filter = ('tipo_combustible', 'empresa', 'tipo_vehiculo')
    search_fields = ('chapa', 'tipo_vehiculo', 'empresa')


@admin.register(DetalleSolicitud)
class DetalleSolicitudAdmin(admin.ModelAdmin):
    list_display = ('solicitud', 'transporte', 'actividad', 'cant_abastecer')