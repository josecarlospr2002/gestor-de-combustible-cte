from django.contrib import admin
from .models import SolicitudCombustible, Transporte, DetalleSolicitud, DespachoCombustible, SuministroCombustible


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


@admin.register(DespachoCombustible)
class DespachoCombustibleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_hora', 'subtotal_consumo', 'subtotal_venta', 'total_general', 'estado')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('nombre',)


@admin.register(SuministroCombustible)
class SuministroCombustibleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_hora', 'tipo_combustible', 'cantidad')
    list_filter = ('tipo_combustible', 'fecha_hora')
    search_fields = ('nombre', 'descripcion')