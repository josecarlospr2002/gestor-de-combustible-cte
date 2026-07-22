from django.contrib import admin
from .models import SolicitudCombustible


@admin.register(SolicitudCombustible)
class SolicitudCombustibleAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitante', 'cantidad_litros', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('solicitante__username', 'motivo')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')