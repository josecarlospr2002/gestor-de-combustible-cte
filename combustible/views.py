from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
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

    nombre = request.GET.get('nombre', '')
    fecha = request.GET.get('fecha', '')
    estado = request.GET.get('estado', '')

    if nombre:
        solicitudes = solicitudes.filter(nombre__icontains=nombre)
    if fecha:
        solicitudes = solicitudes.filter(fecha_hora__date=fecha)
    if estado:
        solicitudes = solicitudes.filter(estado=estado)

    return render(request, 'combustible/lista_solicitudes.html', {'solicitudes': solicitudes})

@login_required
def crear_solicitud(request):
    vehiculos = Transporte.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        descripcion = request.POST.get('descripcion', '')
        vehiculos_quitados = request.POST.get('vehiculos_quitados', '')

        if not fecha_hora:
            messages.error(request, 'La fecha y hora son obligatorias.')
            return render(request, 'combustible/crear_solicitud.html', {
                'vehiculos': vehiculos,
                'nombre_temp': nombre,
                'fecha_hora_temp': fecha_hora,
                'descripcion_temp': descripcion,
                'vehiculos_quitados': vehiculos_quitados,
            })

        # Validar que la fecha no sea futura
        fecha_parseada = parse_datetime(fecha_hora)
        if fecha_parseada:
            if timezone.is_naive(fecha_parseada):
                fecha_parseada = timezone.make_aware(fecha_parseada)
            if fecha_parseada > timezone.now():
                for v in vehiculos:
                    v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                    v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
                messages.error(request, 'No se puede registrar una solicitud con fecha futura.')
                return render(request, 'combustible/crear_solicitud.html', {
                    'vehiculos': vehiculos,
                    'nombre_temp': nombre,
                    'fecha_hora_temp': fecha_hora,
                    'descripcion_temp': descripcion,
                    'vehiculos_quitados': vehiculos_quitados,
                })

        tiene_datos = False
        for vehiculo in vehiculos:
            if str(vehiculo.id) in vehiculos_quitados.split(','):
                continue
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '').strip()
            cant_abastecer = request.POST.get(f'cant_abastecer_{vehiculo.id}', '').strip()

            if actividad and cant_abastecer and cant_abastecer != '0':
                tiene_datos = True
            elif (actividad and not cant_abastecer) or (not actividad and cant_abastecer and cant_abastecer != '0') or (actividad and cant_abastecer == '0'):
                for v in vehiculos:
                    v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                    v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
                messages.error(request, 'Hay campo/s de Actividad o de Cant. a Abastecer sin rellenar.')
                return render(request, 'combustible/crear_solicitud.html', {
                    'vehiculos': vehiculos,
                    'nombre_temp': nombre,
                    'fecha_hora_temp': fecha_hora,
                    'descripcion_temp': descripcion,
                    'vehiculos_quitados': vehiculos_quitados,
                })

        if not tiene_datos:
            for v in vehiculos:
                v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
            messages.error(request, 'Debe llenar al menos un vehículo con ambos campos para guardar la solicitud.')
            return render(request, 'combustible/crear_solicitud.html', {
                'vehiculos': vehiculos,
                'nombre_temp': nombre,
                'fecha_hora_temp': fecha_hora,
                'descripcion_temp': descripcion,
                'vehiculos_quitados': vehiculos_quitados,
            })

        if not nombre:
            nombre = f"Solicitud de Combustible para el día {fecha_hora}"

        solicitud = SolicitudCombustible.objects.create(
            nombre=nombre,
            fecha_hora=fecha_hora,
            descripcion=descripcion,
            estado='borrador'
        )

        for vehiculo in vehiculos:
            if str(vehiculo.id) in vehiculos_quitados.split(','):
                continue
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '').strip()
            cant_abastecer = request.POST.get(f'cant_abastecer_{vehiculo.id}', '0').strip()

            if actividad and cant_abastecer and cant_abastecer != '0':
                DetalleSolicitud.objects.create(
                    solicitud=solicitud,
                    transporte=vehiculo,
                    actividad=actividad,
                    cant_abastecer=float(cant_abastecer)
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

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        descripcion = request.POST.get('descripcion', '')
        vehiculos_quitados = request.POST.get('vehiculos_quitados', '')

        if not fecha_hora:
            for v in vehiculos:
                det = detalles_dict.get(v.id)
                v.actividad_temp = request.POST.get(f'actividad_{v.id}', det.actividad if det else '')
                v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', str(det.cant_abastecer) if det else '')
            messages.error(request, 'La fecha y hora son obligatorias.')
            return render(request, 'combustible/editar_solicitud.html', {
                'solicitud': solicitud,
                'vehiculos': vehiculos,
                'nombre_temp': nombre,
                'fecha_hora_temp': fecha_hora,
                'descripcion_temp': descripcion,
                'vehiculos_quitados': vehiculos_quitados,
            })

        # Validar que la fecha no sea futura
        fecha_parseada = parse_datetime(fecha_hora)
        if fecha_parseada:
            if timezone.is_naive(fecha_parseada):
                fecha_parseada = timezone.make_aware(fecha_parseada)
            if fecha_parseada > timezone.now():
                for v in vehiculos:
                    v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                    v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
                messages.error(request, 'No se puede registrar una solicitud con fecha futura.')
                return render(request, 'combustible/editar_solicitud.html', {
                    'solicitud': solicitud,
                    'vehiculos': vehiculos,
                    'nombre_temp': nombre,
                    'fecha_hora_temp': fecha_hora,
                    'descripcion_temp': descripcion,
                    'vehiculos_quitados': vehiculos_quitados,
                })

        tiene_datos = False
        for vehiculo in vehiculos:
            if str(vehiculo.id) in vehiculos_quitados.split(','):
                continue
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '').strip()
            cant_abastecer = request.POST.get(f'cant_abastecer_{vehiculo.id}', '').strip()

            if actividad and cant_abastecer and cant_abastecer != '0':
                tiene_datos = True
            elif (actividad and not cant_abastecer) or (not actividad and cant_abastecer and cant_abastecer != '0') or (actividad and cant_abastecer == '0'):
                for v in vehiculos:
                    v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                    v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
                messages.error(request, 'Hay campo/s de Actividad o de Cant. a Abastecer sin rellenar.')
                return render(request, 'combustible/editar_solicitud.html', {
                    'solicitud': solicitud,
                    'vehiculos': vehiculos,
                    'nombre_temp': nombre,
                    'fecha_hora_temp': fecha_hora,
                    'descripcion_temp': descripcion,
                    'vehiculos_quitados': vehiculos_quitados,
                })

        if not tiene_datos:
            for v in vehiculos:
                v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
            messages.error(request, 'Debe llenar al menos un vehículo con ambos campos para guardar la solicitud.')
            return render(request, 'combustible/editar_solicitud.html', {
                'solicitud': solicitud,
                'vehiculos': vehiculos,
                'nombre_temp': nombre,
                'fecha_hora_temp': fecha_hora,
                'descripcion_temp': descripcion,
                'vehiculos_quitados': vehiculos_quitados,
            })

        solicitud.nombre = nombre
        solicitud.fecha_hora = fecha_hora
        solicitud.descripcion = descripcion
        solicitud.save()

        detalles.delete()

        for vehiculo in vehiculos:
            if str(vehiculo.id) in vehiculos_quitados.split(','):
                continue
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '').strip()
            cant_abastecer = request.POST.get(f'cant_abastecer_{vehiculo.id}', '0').strip()

            if actividad and cant_abastecer and cant_abastecer != '0':
                DetalleSolicitud.objects.create(
                    solicitud=solicitud,
                    transporte=vehiculo,
                    actividad=actividad,
                    cant_abastecer=float(cant_abastecer)
                )

        messages.success(request, 'Solicitud actualizada correctamente.')
        return redirect('lista_solicitudes')

    # GET: cargar datos guardados
    for v in vehiculos:
        detalle = detalles_dict.get(v.id)
        if detalle:
            v.detalle_actividad = detalle.actividad if detalle.actividad else ''
            v.detalle_cant_abastecer = str(detalle.cant_abastecer) if detalle.cant_abastecer else ''
        else:
            v.detalle_actividad = ''
            v.detalle_cant_abastecer = ''

    return render(request, 'combustible/editar_solicitud.html', {
        'solicitud': solicitud,
        'vehiculos': vehiculos,
    })

@login_required
def aprobar_solicitud(request, pk):
    if request.user.departamento not in ['admin', 'directivo']:
        messages.error(request, 'No tiene permisos para aprobar solicitudes.')
        return redirect('lista_solicitudes')

    solicitud = get_object_or_404(SolicitudCombustible, pk=pk, estado='pendiente')
    solicitud.estado = 'aprobada'
    solicitud.save()
    messages.success(request, f'Solicitud "{solicitud.nombre}" aprobada correctamente.')
    return redirect('lista_solicitudes')

@login_required
def rechazar_solicitud(request, pk):
    if request.user.departamento not in ['admin', 'directivo']:
        messages.error(request, 'No tiene permisos para rechazar solicitudes.')
        return redirect('lista_solicitudes')

    solicitud = get_object_or_404(SolicitudCombustible, pk=pk, estado='pendiente')
    solicitud.estado = 'rechazada'
    solicitud.motivo_rechazo = request.GET.get('motivo', '')
    solicitud.save()
    messages.success(request, f'Solicitud "{solicitud.nombre}" rechazada.')
    return redirect('lista_solicitudes')

@login_required
def eliminar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk, estado='borrador')
    solicitud.delete()
    messages.success(request, 'Solicitud eliminada correctamente.')
    return redirect('lista_solicitudes')