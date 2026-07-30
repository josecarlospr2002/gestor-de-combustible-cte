from django.contrib import admin
from .models import SolicitudCombustible, Transporte, DetalleSolicitud

@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_display = (
        'empresa',
        'tipo_vehiculo',
        'chapa',
        'tipo_combustible'
    )
    list_filter = ('tipo_combustible', 'empresa', 'tipo_vehiculo')
    search_fields = ('chapa',)

@admin.register(SolicitudCombustible)
class SolicitudCombustibleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'solicitante',
        'motivo',
        'estado',
        'fecha_creacion'
    )
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('solicitante__username', 'motivo')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')

@admin.register(DetalleSolicitud)
class DetalleSolicitudAdmin(admin.ModelAdmin):
    list_display = (
        'solicitud',
        'transporte',
        'actividad',
        'via_blanca',
        'cte',
        'ic'
    )