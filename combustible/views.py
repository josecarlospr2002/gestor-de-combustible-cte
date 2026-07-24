from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SolicitudCombustible, Transporte


@login_required
def dashboard(request):
    return render(request, 'combustible/dashboard.html')

@login_required
def lista_transporte(request):
    vehiculos = Transporte.objects.all()
    return render(request, 'combustible/lista_transporte.html', {'vehiculos': vehiculos})