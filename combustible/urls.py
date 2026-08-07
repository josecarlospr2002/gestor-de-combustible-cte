from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('transporte/', views.lista_transporte, name='lista_transporte'),
    path('transporte/crear/', views.crear_vehiculo, name='crear_vehiculo'),
    path('transporte/editar/<int:pk>/', views.editar_vehiculo, name='editar_vehiculo'),
    path('transporte/eliminar/<int:pk>/', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    path('solicitudes/crear/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitudes/enviar/<int:pk>/', views.enviar_solicitud, name='enviar_solicitud'),
    path('solicitudes/ver/<int:pk>/', views.ver_solicitud, name='ver_solicitud'),
    path('solicitudes/editar/<int:pk>/', views.editar_solicitud, name='editar_solicitud'),
    path('solicitudes/eliminar/<int:pk>/', views.eliminar_solicitud, name='eliminar_solicitud'),
    path('solicitudes/aprobar/<int:pk>/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('solicitudes/rechazar/<int:pk>/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('despachos/', views.lista_despachos, name='lista_despachos'),
]