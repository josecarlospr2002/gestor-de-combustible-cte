from django.db import models
from django.conf import settings


class Transporte(models.Model):
    tipo_combustible = models.CharField(max_length=50, verbose_name='Tipo de Combustible')
    empresa = models.CharField(max_length=50, verbose_name='Empresa')
    tipo_vehiculo = models.CharField(max_length=50, verbose_name='Tipo de Vehículo')
    chapa = models.CharField(max_length=50, verbose_name='Chapa')
    ic = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='I/C')

    class Meta:
        verbose_name = 'Transporte'
        verbose_name_plural = 'Transportes'
        ordering = ['empresa']

    def __str__(self):
        return f"{self.tipo_vehiculo} - {self.chapa}"


class SolicitudCombustible(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobada', 'Aprobada por Director'),
        ('rechazada', 'Rechazada por Director'),
    ]

    nombre = models.CharField(max_length=100, blank=True, verbose_name='Nombre de la Solicitud')
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    estado = models.CharField(max_length=30, choices=ESTADOS, default='borrador')
    motivo_rechazo = models.TextField(blank=True, null=True, verbose_name='Motivo del Rechazo')

    class Meta:
        verbose_name = 'Solicitud de Combustible'
        verbose_name_plural = 'Solicitudes de Combustible'
        ordering = ['-fecha_hora']

    def __str__(self):
        if self.nombre:
            return self.nombre
        return f"Solicitud #{self.id} - {self.fecha_hora.strftime('%d/%m/%Y')}"


class DetalleSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudCombustible, on_delete=models.CASCADE, related_name='detalles')
    transporte = models.ForeignKey(Transporte, on_delete=models.CASCADE, verbose_name='Vehículo')
    actividad = models.CharField(max_length=50, verbose_name='Actividad')
    cant_abastecer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Cant. a Abastecer')

    class Meta:
        verbose_name = 'Detalle de Solicitud'
        verbose_name_plural = 'Detalles de Solicitudes'

    def __str__(self):
        return f"{self.transporte.chapa} - {self.solicitud}"