from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Case, When, Value, IntegerField
from decimal import Decimal, InvalidOperation
from .models import Transporte, SolicitudCombustible, DetalleSolicitud, DespachoCombustible, SuministroCombustible, \
    RecepcionAlmacen
from .forms import TransporteForm, SuministroCombustibleForm

CANTIDAD_MAXIMA = Decimal('9999999999.99')


def get_vehiculos_ordenados():
    """Retorna todos los vehículos con el orden personalizado."""
    return Transporte.objects.all().annotate(
        orden_combustible=Case(
            When(tipo_combustible__icontains='gasolina', then=Value(1)),
            When(tipo_combustible__icontains='regular', then=Value(1)),
            When(tipo_combustible__icontains='diésel', then=Value(2)),
            When(tipo_combustible__icontains='diesel', then=Value(2)),
            When(tipo_combustible__icontains='petróleo', then=Value(2)),
            When(tipo_combustible__icontains='petroleo', then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        ),
        orden_empresa=Case(
            When(empresa__iexact='CTE', then=Value(1)),
            When(empresa__iexact='AUSA', then=Value(2)),
            When(empresa__iexact='UCM', then=Value(3)),
            When(empresa__iexact='ETEP', then=Value(4)),
            When(empresa__iexact='EMCE', then=Value(5)),
            When(empresa__iexact='TAXI', then=Value(6)),
            default=Value(7),
            output_field=IntegerField(),
        ),
        orden_vehiculo=Case(
            When(tipo_vehiculo__icontains='auto', then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        ),
    ).order_by('orden_combustible', 'orden_empresa', 'orden_vehiculo')


@login_required
def dashboard(request):
    from .models import SuministroCombustible
    from django.db.models import Sum

    total_combustible = SuministroCombustible.objects.filter(
        estado='validado'
    ).aggregate(
        total=Sum('cantidad')
    )['total'] or 0

    return render(request, 'combustible/dashboard.html', {
        'total_combustible': total_combustible,
    })


@login_required
def lista_transporte(request):
    vehiculos = get_vehiculos_ordenados()

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


def _validar_cantidad(cant_str):
    """Valida que la cantidad sea un decimal válido y no exceda el máximo."""
    try:
        cantidad = Decimal(cant_str)
        if cantidad <= 0:
            return None, 'La cantidad debe ser mayor que 0.'
        if cantidad > CANTIDAD_MAXIMA:
            return None, f'La cantidad no puede exceder {CANTIDAD_MAXIMA}.'
        return cantidad, None
    except InvalidOperation:
        return None, 'Cantidad inválida.'


@login_required
def crear_solicitud(request):
    vehiculos = get_vehiculos_ordenados()

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

        # Validar cantidades
        error_cantidad = False
        tiene_datos = False
        for vehiculo in vehiculos:
            if str(vehiculo.id) in vehiculos_quitados.split(','):
                continue
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '').strip()
            cant_str = request.POST.get(f'cant_abastecer_{vehiculo.id}', '').strip()

            if actividad and cant_str and cant_str != '0':
                cantidad, error = _validar_cantidad(cant_str)
                if error:
                    for v in vehiculos:
                        v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                        v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
                    messages.error(request, f'Error en {vehiculo.chapa}: {error}')
                    error_cantidad = True
                    break
                tiene_datos = True
            elif (actividad and not cant_str) or (not actividad and cant_str and cant_str != '0') or (
                    actividad and cant_str == '0'):
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

        if error_cantidad:
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
            cant_str = request.POST.get(f'cant_abastecer_{vehiculo.id}', '0').strip()

            if actividad and cant_str and cant_str != '0':
                cantidad, _ = _validar_cantidad(cant_str)
                if cantidad:
                    DetalleSolicitud.objects.create(
                        solicitud=solicitud,
                        transporte=vehiculo,
                        actividad=actividad,
                        cant_abastecer=cantidad
                    )

        messages.success(request, 'Solicitud creada correctamente.')
        return redirect('lista_solicitudes')

    return render(request, 'combustible/crear_solicitud.html', {'vehiculos': vehiculos})


@login_required
def enviar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk)
    if solicitud.estado in ['borrador', 'rechazada']:
        solicitud.estado = 'pendiente'
        solicitud.save()
        messages.success(request, 'Solicitud enviada correctamente.')
    else:
        messages.error(request, 'Esta solicitud no se puede enviar.')
    return redirect('lista_solicitudes')


@login_required
def ver_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk)
    detalles = DetalleSolicitud.objects.filter(solicitud=solicitud).select_related('transporte')

    # Calcular resumen por empresa
    resumen_consumo = {}
    resumen_venta = {}
    subtotal_consumo = 0
    subtotal_venta = 0

    for detalle in detalles:
        empresa = detalle.transporte.empresa
        cantidad = detalle.cant_abastecer
        if empresa.lower() in ['cte', 'ausa', 'ucm']:
            resumen_consumo[empresa] = resumen_consumo.get(empresa, 0) + cantidad
            subtotal_consumo += cantidad
        else:
            resumen_venta[empresa] = resumen_venta.get(empresa, 0) + cantidad
            subtotal_venta += cantidad

    # Ordenar alfabéticamente
    resumen_consumo = dict(sorted(resumen_consumo.items()))
    resumen_venta = dict(sorted(resumen_venta.items()))
    total_general = subtotal_consumo + subtotal_venta

    return render(request, 'combustible/ver_solicitud.html', {
        'solicitud': solicitud,
        'detalles': detalles,
        'resumen_consumo': resumen_consumo,
        'resumen_venta': resumen_venta,
        'subtotal_consumo': subtotal_consumo,
        'subtotal_venta': subtotal_venta,
        'total_general': total_general,
    })


@login_required
def editar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk)
    if solicitud.estado not in ['borrador', 'rechazada']:
        messages.error(request, 'Esta solicitud no se puede editar.')
        return redirect('lista_solicitudes')

    vehiculos = get_vehiculos_ordenados()
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
                v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}',
                                                         str(det.cant_abastecer) if det else '')
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

        # Validar cantidades
        error_cantidad = False
        tiene_datos = False
        for vehiculo in vehiculos:
            if str(vehiculo.id) in vehiculos_quitados.split(','):
                continue
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '').strip()
            cant_str = request.POST.get(f'cant_abastecer_{vehiculo.id}', '').strip()

            if actividad and cant_str and cant_str != '0':
                cantidad, error = _validar_cantidad(cant_str)
                if error:
                    for v in vehiculos:
                        v.actividad_temp = request.POST.get(f'actividad_{v.id}', '')
                        v.cant_abastecer_temp = request.POST.get(f'cant_abastecer_{v.id}', '')
                    messages.error(request, f'Error en {vehiculo.chapa}: {error}')
                    error_cantidad = True
                    break
                tiene_datos = True
            elif (actividad and not cant_str) or (not actividad and cant_str and cant_str != '0') or (
                    actividad and cant_str == '0'):
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

        if error_cantidad:
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
        solicitud.estado = 'borrador'
        solicitud.save()

        detalles.delete()

        for vehiculo in vehiculos:
            if str(vehiculo.id) in vehiculos_quitados.split(','):
                continue
            actividad = request.POST.get(f'actividad_{vehiculo.id}', '').strip()
            cant_str = request.POST.get(f'cant_abastecer_{vehiculo.id}', '0').strip()

            if actividad and cant_str and cant_str != '0':
                cantidad, _ = _validar_cantidad(cant_str)
                if cantidad:
                    DetalleSolicitud.objects.create(
                        solicitud=solicitud,
                        transporte=vehiculo,
                        actividad=actividad,
                        cant_abastecer=cantidad
                    )

        messages.success(request, 'Solicitud actualizada correctamente.')
        return redirect('lista_solicitudes')

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

    # Calcular totales
    detalles = DetalleSolicitud.objects.filter(solicitud=solicitud)
    subtotal_consumo = 0
    subtotal_venta = 0

    for detalle in detalles:
        empresa = detalle.transporte.empresa
        cantidad = detalle.cant_abastecer
        if empresa.lower() in ['cte', 'ausa', 'ucm']:
            subtotal_consumo += cantidad
        else:
            subtotal_venta += cantidad

    total_general = subtotal_consumo + subtotal_venta

    # Crear despacho
    DespachoCombustible.objects.create(
        solicitud=solicitud,
        nombre=solicitud.nombre,
        fecha_hora=solicitud.fecha_hora,
        subtotal_consumo=subtotal_consumo,
        subtotal_venta=subtotal_venta,
        total_general=total_general,
        estado='pendiente'
    )

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
    solicitud = get_object_or_404(SolicitudCombustible, pk=pk)
    if solicitud.estado not in ['borrador', 'rechazada']:
        messages.error(request, 'Esta solicitud no se puede eliminar.')
        return redirect('lista_solicitudes')
    solicitud.delete()
    messages.success(request, 'Solicitud eliminada correctamente.')
    return redirect('lista_solicitudes')


@login_required
def lista_despachos(request):
    if request.user.departamento not in ['admin', 'directivo', 'petroleo']:
        messages.error(request, 'No tiene permisos para ver los despachos.')
        return redirect('dashboard')

    despachos = DespachoCombustible.objects.all()

    # Filtros
    nombre = request.GET.get('nombre', '')
    fecha = request.GET.get('fecha', '')
    estado = request.GET.get('estado', '')

    if nombre:
        despachos = despachos.filter(nombre__icontains=nombre)
    if fecha:
        despachos = despachos.filter(fecha_hora__date=fecha)
    if estado:
        despachos = despachos.filter(estado=estado)

    return render(request, 'combustible/lista_despachos.html', {'despachos': despachos})


@login_required
def crear_suministro(request):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('dashboard')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        tipo_combustible = request.POST.get('tipo_combustible', '')
        cantidad_str = request.POST.get('cantidad', '')
        descripcion = request.POST.get('descripcion', '')

        if not fecha_hora:
            messages.error(request, 'La fecha y hora son obligatorias.')
            return render(request, 'combustible/crear_suministro.html', {
                'form': SuministroCombustibleForm(request.POST)
            })

        if not tipo_combustible:
            messages.error(request, 'El tipo de combustible es obligatorio.')
            return render(request, 'combustible/crear_suministro.html', {
                'form': SuministroCombustibleForm(request.POST)
            })

        # Validar que la fecha no sea futura
        fecha_parseada = parse_datetime(fecha_hora)
        if fecha_parseada:
            if timezone.is_naive(fecha_parseada):
                fecha_parseada = timezone.make_aware(fecha_parseada)
            if fecha_parseada > timezone.now():
                messages.error(request, 'No se puede registrar un suministro con fecha futura.')
                return render(request, 'combustible/crear_suministro.html', {
                    'form': SuministroCombustibleForm(request.POST)
                })

        # Validar cantidad
        cantidad, error = _validar_cantidad(cantidad_str)
        if error:
            messages.error(request, error)
            return render(request, 'combustible/crear_suministro.html', {
                'form': SuministroCombustibleForm(request.POST)
            })

        if not nombre:
            nombre = f"Suministro de Combustible del día {fecha_hora}"

        SuministroCombustible.objects.create(
            nombre=nombre,
            fecha_hora=fecha_hora,
            tipo_combustible=tipo_combustible,
            cantidad=cantidad,
            descripcion=descripcion
        )

        messages.success(request, 'Suministro registrado correctamente.')
        return redirect('lista_suministros')

    return render(request, 'combustible/crear_suministro.html', {
        'form': SuministroCombustibleForm()
    })


@login_required
def lista_suministros(request):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para ver los suministros.')
        return redirect('dashboard')

    suministros = SuministroCombustible.objects.all()

    # Filtros
    nombre = request.GET.get('nombre', '')
    fecha = request.GET.get('fecha', '')
    tipo_combustible = request.GET.get('tipo_combustible', '')

    if nombre:
        suministros = suministros.filter(nombre__icontains=nombre)
    if fecha:
        suministros = suministros.filter(fecha_hora__date=fecha)
    if tipo_combustible:
        suministros = suministros.filter(tipo_combustible__icontains=tipo_combustible)

    return render(request, 'combustible/lista_suministros.html', {'suministros': suministros})


@login_required
def editar_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('dashboard')

    suministro = get_object_or_404(SuministroCombustible, pk=pk)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        tipo_combustible = request.POST.get('tipo_combustible', '')
        cantidad_str = request.POST.get('cantidad', '')
        descripcion = request.POST.get('descripcion', '')

        if not fecha_hora:
            messages.error(request, 'La fecha y hora son obligatorias.')
            return render(request, 'combustible/editar_suministro.html', {'suministro': suministro})

        if not tipo_combustible:
            messages.error(request, 'El tipo de combustible es obligatorio.')
            return render(request, 'combustible/editar_suministro.html', {'suministro': suministro})

        # Validar que la fecha no sea futura
        fecha_parseada = parse_datetime(fecha_hora)
        if fecha_parseada:
            if timezone.is_naive(fecha_parseada):
                fecha_parseada = timezone.make_aware(fecha_parseada)
            if fecha_parseada > timezone.now():
                messages.error(request, 'No se puede registrar un suministro con fecha futura.')
                return render(request, 'combustible/editar_suministro.html', {'suministro': suministro})

        # Validar cantidad
        cantidad, error = _validar_cantidad(cantidad_str)
        if error:
            messages.error(request, error)
            return render(request, 'combustible/editar_suministro.html', {'suministro': suministro})

        if not nombre:
            nombre = f"Suministro de Combustible del día {fecha_hora}"

        suministro.nombre = nombre
        suministro.fecha_hora = fecha_hora
        suministro.tipo_combustible = tipo_combustible
        suministro.cantidad = cantidad
        suministro.descripcion = descripcion
        suministro.save()

        messages.success(request, 'Suministro modificado correctamente.')
        return redirect('lista_suministros')

    return render(request, 'combustible/editar_suministro.html', {'suministro': suministro})


@login_required
def eliminar_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('dashboard')

    suministro = get_object_or_404(SuministroCombustible, pk=pk)
    suministro.delete()
    messages.success(request, 'Suministro eliminado correctamente.')
    return redirect('lista_suministros')


@login_required
def ver_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para ver este suministro.')
        return redirect('dashboard')

    suministro = get_object_or_404(SuministroCombustible, pk=pk)
    return render(request, 'combustible/ver_suministro.html', {'suministro': suministro})


@login_required
def validar_suministro(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('dashboard')

    suministro = get_object_or_404(SuministroCombustible, pk=pk, estado='pendiente')
    suministro.estado = 'validado'
    suministro.save()
    messages.success(request, f'Suministro "{suministro.nombre}" validado correctamente.')
    return redirect('lista_suministros')


@login_required
def lista_almacen(request):
    if request.user.departamento not in ['admin', 'almacen']:
        messages.error(request, 'No tiene permisos para ver el almacén.')
        return redirect('dashboard')

    recepciones = RecepcionAlmacen.objects.all()

    nombre = request.GET.get('nombre', '')
    fecha = request.GET.get('fecha', '')

    if nombre:
        recepciones = recepciones.filter(despacho__nombre__icontains=nombre)
    if fecha:
        recepciones = recepciones.filter(despacho__fecha_hora__date=fecha)

    return render(request, 'combustible/lista_almacen.html', {'recepciones': recepciones})


@login_required
def ver_almacen(request, pk):
    if request.user.departamento not in ['admin', 'almacen']:
        messages.error(request, 'No tiene permisos para ver esta recepción.')
        return redirect('dashboard')

    recepcion = get_object_or_404(RecepcionAlmacen, pk=pk)
    solicitud = recepcion.despacho.solicitud
    detalles = DetalleSolicitud.objects.filter(solicitud=solicitud).select_related('transporte')

    resumen_consumo = {}
    resumen_venta = {}
    subtotal_consumo = 0
    subtotal_venta = 0

    for detalle in detalles:
        empresa = detalle.transporte.empresa
        cantidad = detalle.cant_abastecer
        if empresa.lower() in ['cte', 'ausa', 'ucm']:
            resumen_consumo[empresa] = resumen_consumo.get(empresa, 0) + cantidad
            subtotal_consumo += cantidad
        else:
            resumen_venta[empresa] = resumen_venta.get(empresa, 0) + cantidad
            subtotal_venta += cantidad

    resumen_consumo = dict(sorted(resumen_consumo.items()))
    resumen_venta = dict(sorted(resumen_venta.items()))
    total_general = subtotal_consumo + subtotal_venta

    return render(request, 'combustible/ver_almacen.html', {
        'recepcion': recepcion,
        'solicitud': solicitud,
        'detalles': detalles,
        'resumen_consumo': resumen_consumo,
        'resumen_venta': resumen_venta,
        'subtotal_consumo': subtotal_consumo,
        'subtotal_venta': subtotal_venta,
        'total_general': total_general,
    })


@login_required
def confirmar_recepcion(request, pk):
    if request.user.departamento not in ['admin', 'almacen']:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('dashboard')

    recepcion = get_object_or_404(RecepcionAlmacen, pk=pk, estado='pendiente')
    recepcion.estado = 'recibido'
    recepcion.save()

    recepcion.despacho.estado = 'suministrado'
    recepcion.despacho.save()

    messages.success(request, f'Recepción "{recepcion.despacho.nombre}" confirmada en almacén.')
    return redirect('lista_almacen')


@login_required
def confirmar_extraccion(request, pk):
    if request.user.departamento not in ['admin', 'petroleo']:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('dashboard')

    despacho = get_object_or_404(DespachoCombustible, pk=pk, estado='pendiente')
    despacho.estado = 'extraido'
    despacho.save()

    # Crear la recepción para almacén
    RecepcionAlmacen.objects.create(
        despacho=despacho
    )

    messages.success(request, f'Combustible extraído. Recepción enviada a almacén.')
    return redirect('lista_despachos')
