from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Transporte, SolicitudCombustible, DetalleSolicitud
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


@login_required
def lista_solicitudes(request):
    solicitudes = SolicitudCombustible.objects.all()
    return render(request, 'combustible/lista_solicitudes.html', {'solicitudes': solicitudes})


@login_required
def crear_solicitud(request):
    vehiculos = Transporte.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        descripcion = request.POST.get('descripcion', '')

        if not fecha_hora:
            messages.error(request, 'La fecha y hora son obligatorias.')
            return render(request, 'combustible/crear_solicitud.html', {'vehiculos': vehiculos})

        tiene_datos = False
        for vehiculo in vehiculos:
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '')
            via_blanca = request.POST.get(f'via_blanca_{vehiculo.id}', '')
            cte = request.POST.get(f'cte_{vehiculo.id}', '')
            ic = request.POST.get(f'ic_{vehiculo.id}', '')
            if actividad or via_blanca or cte or ic:
                tiene_datos = True
                break

        if not tiene_datos:
            messages.error(request, 'Debe llenar al menos un vehículo para enviar la solicitud.')
            return render(request, 'combustible/crear_solicitud.html', {'vehiculos': vehiculos})

        if not nombre:
            nombre = f"Solicitud de Combustible para el día {fecha_hora}"

        solicitud = SolicitudCombustible.objects.create(
            nombre=nombre,
            fecha_hora=fecha_hora,
            descripcion=descripcion,
            estado='borrador'
        )

        for vehiculo in vehiculos:
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '')
            via_blanca = request.POST.get(f'via_blanca_{vehiculo.id}', '0')
            cte = request.POST.get(f'cte_{vehiculo.id}', '0')
            ic = request.POST.get(f'ic_{vehiculo.id}', '0')

            if actividad or via_blanca != '0' or cte != '0' or ic != '0':
                DetalleSolicitud.objects.create(
                    solicitud=solicitud,
                    transporte=vehiculo,
                    actividad=actividad,
                    via_blanca=float(via_blanca) if via_blanca else 0,
                    cte=float(cte) if cte else 0,
                    ic=float(ic) if ic else 0
                )

        messages.success(request, 'Solicitud creada correctamente.')
        return redirect('lista_solicitudes')

    return render(request, 'combustible/crear_solicitud.html', {'vehiculos': vehiculos})


@login_required
def enviar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk)
    if solicitud.estado == 'borrador':
        solicitud.estado = 'pendiente'
        solicitud.save()
        messages.success(request, 'Solicitud enviada correctamente.')
    return redirect('lista_solicitudes')


@login_required
def ver_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk)
    detalles = DetalleSolicitud.objects.filter(solicitud=solicitud)
    return render(request, 'combustible/ver_solicitud.html', {
        'solicitud': solicitud,
        'detalles': detalles
    })


@login_required
def editar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk, estado='borrador')
    vehiculos = Transporte.objects.all()
    detalles = DetalleSolicitud.objects.filter(solicitud=solicitud)

    detalles_dict = {}
    for d in detalles:
        detalles_dict[d.transporte_id] = d

    for v in vehiculos:
        detalle = detalles_dict.get(v.id)
        if detalle:
            v.detalle_actividad = detalle.actividad if detalle.actividad else ''
            v.detalle_via_blanca = str(detalle.via_blanca) if detalle.via_blanca else '0'
            v.detalle_cte = str(detalle.cte) if detalle.cte else '0'
            v.detalle_ic = str(detalle.ic) if detalle.ic else '0'
        else:
            v.detalle_actividad = ''
            v.detalle_via_blanca = '0'
            v.detalle_cte = '0'
            v.detalle_ic = '0'

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        descripcion = request.POST.get('descripcion', '')

        solicitud.nombre = nombre
        solicitud.fecha_hora = fecha_hora
        solicitud.descripcion = descripcion
        solicitud.save()

        detalles.delete()

        for vehiculo in vehiculos:
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '')
            via_blanca = request.POST.get(f'via_blanca_{vehiculo.id}', '0')
            cte = request.POST.get(f'cte_{vehiculo.id}', '0')
            ic = request.POST.get(f'ic_{vehiculo.id}', '0')

            if actividad or via_blanca != '0' or cte != '0' or ic != '0':
                DetalleSolicitud.objects.create(
                    solicitud=solicitud,
                    transporte=vehiculo,
                    actividad=actividad,
                    via_blanca=float(via_blanca) if via_blanca else 0,
                    cte=float(cte) if cte else 0,
                    ic=float(ic) if ic else 0
                )

        messages.success(request, 'Solicitud actualizada correctamente.')
        return redirect('lista_solicitudes')

    return render(request, 'combustible/editar_solicitud.html', {
        'solicitud': solicitud,
        'vehiculos': vehiculos,
    })


@login_required
def eliminar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk, estado='borrador')
    solicitud.delete()
    messages.success(request, 'Solicitud eliminada correctamente.')
    return redirect('lista_solicitudes')