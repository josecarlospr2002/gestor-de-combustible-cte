from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    DEPARTAMENTOS = [
        ('admin', 'Administrador del Sistema'),
        ('transporte', 'Departamento de Transporte'),
        ('directivo', 'Director General / Técnico'),
        ('petroleo', 'Departamento de Petróleo'),
        ('almacen', 'Almacén'),
        ('random', 'Usuario Externo'),
    ]

    departamento = models.CharField(
        max_length=20,
        choices=DEPARTAMENTOS,
        default='random',
        verbose_name='Departamento / Rol'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} - {self.get_departamento_display()}"