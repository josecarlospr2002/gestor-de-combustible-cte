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
    cant_abastecer = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Cant. a Abastecer')

    class Meta:
        verbose_name = 'Detalle de Solicitud'
        verbose_name_plural = 'Detalles de Solicitudes'

    def __str__(self):
        return f"{self.transporte.chapa} - {self.solicitud}"


class DespachoCombustible(models.Model):
    ESTADOS_DESPACHO = [
        ('pendiente', 'Pendiente de Extracción'),
        ('extraido', 'Combustible Extraído'),
        ('suministrado', 'Suministrado a Vehículos'),
    ]

    solicitud = models.OneToOneField(SolicitudCombustible, on_delete=models.CASCADE, related_name='despacho')
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Solicitud')
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    subtotal_consumo = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           verbose_name='Subtotal de Consumo')
    subtotal_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Subtotal de Venta')
    total_general = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total General')
    estado = models.CharField(max_length=20, choices=ESTADOS_DESPACHO, default='pendiente',
                              verbose_name='Estado del Despacho')

    class Meta:
        verbose_name = 'Despacho de Combustible'
        verbose_name_plural = 'Despachos de Combustible'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Despacho: {self.nombre} - {self.fecha_hora.strftime('%d/%m/%Y')}"


class SuministroCombustible(models.Model):
    ESTADOS_SUMINISTRO = [
        ('pendiente', 'Pendiente de Validar'),
        ('validado', 'Validado'),
    ]

    nombre = models.CharField(max_length=100, blank=True, verbose_name='Nombre del Suministro')
    fecha_hora = models.DateTimeField(verbose_name='Fecha y Hora')
    tipo_combustible = models.CharField(max_length=50, verbose_name='Tipo de Combustible')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Cantidad de Combustible')
    estado = models.CharField(max_length=20, choices=ESTADOS_SUMINISTRO, default='pendiente', verbose_name='Estado')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción / Nota')


class RecepcionAlmacen(models.Model):
    ESTADOS_ALMACEN = [
        ('pendiente', 'Pendiente de Recepción'),
        ('recibido', 'Recibido en Almacén'),
    ]

    despacho = models.OneToOneField(DespachoCombustible, on_delete=models.CASCADE, related_name='recepcion_almacen')
    estado = models.CharField(max_length=20, choices=ESTADOS_ALMACEN, default='pendiente', verbose_name='Estado')

    class Meta:
        verbose_name = 'Recepción de Almacén'
        verbose_name_plural = 'Recepciones de Almacén'

    def __str__(self):
        return f"Almacén: {self.despacho.nombre}"
