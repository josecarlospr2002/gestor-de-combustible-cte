from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transporte
from .forms import TransporteForm

@login_required
def dashboard(request):
    return render(request, 'combustible/dashboard.html')

@login_required
def lista_transporte(request):
    vehiculos = Transporte.objects.all()

    chapa = request.GET.get('chapa', '')
    tipo_vehiculo = request.GET.get('tipo_vehiculo', '')
    tipo_combustible = request.GET.get('tipo_combustible', '')
    empresa = request.GET.get('empresa', '')

    if chapa:
        vehiculos = vehiculos.filter(chapa__icontains=chapa)
    if tipo_vehiculo:
        vehiculos = vehiculos.filter(tipo_vehiculo__icontains=tipo_vehiculo)
    if tipo_combustible:
        vehiculos = vehiculos.filter(tipo_combustible__icontains=tipo_combustible)
    if empresa:
        vehiculos = vehiculos.filter(empresa__icontains=empresa)

    return render(request, 'combustible/lista_transporte.html', {'vehiculos': vehiculos})

@login_required
def crear_vehiculo(request):
    if request.method == 'POST':
        form = TransporteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehículo agregado correctamente.')
            return redirect('lista_transporte')
        else:
            messages.error(request, 'Rellene todos los campos, por favor.')
    else:
        form = TransporteForm()

    return render(request, 'combustible/crear_vehiculo.html', {'form': form})

@login_required
def editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Transporte, pk=pk)
    if request.method == 'POST':
        form = TransporteForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro modificado correctamente.')
            return redirect('lista_transporte')
        else:
            messages.error(request, 'Rellene todos los campos, por favor.')
    else:
        form = TransporteForm(instance=vehiculo)

    return render(request, 'combustible/editar_vehiculo.html', {'form': form, 'vehiculo': vehiculo})

@login_required
def eliminar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Transporte, pk=pk)
    vehiculo.delete()
    messages.success(request, 'Vehículo eliminado correctamente.')
    return redirect('lista_transporte')