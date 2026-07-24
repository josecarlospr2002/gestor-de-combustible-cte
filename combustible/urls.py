from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    #path('solicitud/crear/', views.crear_solicitud, name='crear_solicitud'),
    path('transporte/', views.lista_transporte, name='lista_transporte'),
]