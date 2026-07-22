from django.db import models
from django.conf import settings


class SolicitudCombustible(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobada', 'Aprobada por Director'),
        ('rechazada', 'Rechazada por Director'),
        ('en_proceso_petroleo', 'En Proceso - Dpto. Petróleo'),
        ('enviada_almacen', 'Enviada a Almacén'),
        ('distribuida', 'Combustible Distribuido'),
    ]

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )
    cantidad_litros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad de Combustible (Litros)'
    )
    motivo = models.TextField(verbose_name='Motivo de la Solicitud')
    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default='borrador'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    director = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aprobaciones'
    )
    comentario_director = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Solicitud de Combustible'
        verbose_name_plural = 'Solicitudes de Combustible'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.solicitante} - {self.estado}"