from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Cliente, Ticket, Estado, CategoriaProblema, Prioridad, Imagen, TicketsArchivados
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .forms import TicketForm

def menu(request):
    return render(request, 'menu_principal.html')

def status(request):
    return render(request, 'status.html')

def abrirticket(request):
    # Obtener los datos de clientes y productos para el formulario
    categorias = CategoriaProblema.objects.all()
    prioridades = Prioridad.objects.all()
    
    today = timezone.now().date()  # Obtener la fecha de hoy
    
    return render(request, 'abrirticket.html', {'categorias': categorias, 'prioridades': prioridades, 'today': today})

def guardar_ticket(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_cliente = request.POST.get('nombre_cliente')
        correo_cliente = request.POST.get('correo_cliente')
        numero_cliente = request.POST.get('numero_cliente')
        categoria_id = request.POST.get('categoria')
        prioridad_id = request.POST.get('prioridad')
        detalle = request.POST.get('detalle')
        imagen = request.FILES.get('imagen')
        fecha_creacion = request.POST.get('fecha_creacion')
        fecha_creacion = datetime.strptime(fecha_creacion, '%Y-%m-%d').date()

        # Validaciones
        if not nombre_cliente or not correo_cliente or not numero_cliente:
            messages.error(request, "Todos los campos del cliente son obligatorios.")
            return redirect('abrir_ticket')

        try:
            cliente, created = Cliente.objects.get_or_create(
                nombre=nombre_cliente,
                email=correo_cliente,
                telefono=numero_cliente
            )

            estado = Estado.objects.get(nombre="En espera")
            categoria = CategoriaProblema.objects.get(id=categoria_id)
            prioridad = Prioridad.objects.get(id=prioridad_id)

            ticket = Ticket(
                cliente=cliente,
                categoria=categoria,
                estado=estado,
                prioridad=prioridad,
                detalle=detalle,
                fecha_creacion=fecha_creacion
            )
            ticket.save()

            if imagen:
                imagen_obj = Imagen(
                    ticket=ticket,
                    imagen=imagen
                )
                imagen_obj.save()

            # Mensaje de éxito
            messages.success(request, f"Ticket creado para {nombre_cliente} con ID {ticket.id}")
            return redirect('abrir_ticket')
        except Exception as e:
            # Mensaje de error
            messages.error(request, f"No se pudo registrar el ticket. Error: {e}")
            return redirect('abrir_ticket')

def buscar_status_por_id_compuesto(request):
    id_compuesto = request.GET.get('id_compuesto')
    status = None

    if id_compuesto:
        try:
            status = Ticket.objects.get(id=id_compuesto)
        except Ticket.DoesNotExist:
            status = None

    return render(request, 'status.html', {'status': status, 'id_compuesto': id_compuesto})

def ticket_list(request):
    query = Ticket.objects.all()

    # Filtros dinámicos
    cliente_id = request.GET.get('cliente', '')
    categoria_id = request.GET.get('categoria', '')
    estado_id = request.GET.get('estado', '')
    prioridad_id = request.GET.get('prioridad', '')

    # filtrito
    if cliente_id:
        query = query.filter(cliente_id=cliente_id)
    if categoria_id:
        query = query.filter(categoria_id=categoria_id)
    if estado_id:
        query = query.filter(estado_id=estado_id)
    if prioridad_id:
        query = query.filter(prioridad_id=prioridad_id)

    # pa que jale los datos del filtro
    clientes = Cliente.objects.all()
    categorias = CategoriaProblema.objects.all()
    estados = Estado.objects.all()
    prioridades = Prioridad.objects.all()
    tickets_archivados = TicketsArchivados.objects.all()

    return render(request, 'ticket_list.html', {
        'tickets': query,
        'clientes': clientes,
        'categorias': categorias,
        'estados': estados,
        'prioridades': prioridades,
        'tickets_archivados': tickets_archivados,
    })

def ticket_create(request):
    if request.method == 'POST':
        # Obtener datos del form
        nombre = request.POST.get('nombre')
        email = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        categoria_id = request.POST.get('categoria')
        prioridad_id = request.POST.get('prioridad')
        detalle = request.POST.get('detalle')
        imagen = request.FILES.get('imagen')  # ESTA COCHINADA NO VOVLVIO A JALA

        if not nombre:
            messages.error(request, "El nombre del cliente es obligatorio.")
            return redirect('ticket_create')

        # Buscar o crear al cliente
        cliente, created = Cliente.objects.get_or_create(
            nombre=nombre,
            defaults={'email': email, 'telefono': telefono}
        )

        # Crear el ticket SIN LA IMAGEN
        ticket = Ticket.objects.create(
            cliente=cliente,
            categoria_id=categoria_id,
            prioridad_id=prioridad_id,
            detalle=detalle,
            estado_id=1  
        )

        # Si hay una imagen, crear la instancia de Imagen asociada al ticket
        if imagen:
            imagen_obj = Imagen.objects.create(
                ticket=ticket,
                imagen=imagen
            )

        messages.success(request, "Ticket creado con éxito.")
        return redirect('ticket_list')

  
    categorias = CategoriaProblema.objects.all()
    prioridades = Prioridad.objects.all()

    return render(request, 'ticket_create.html', {
        'categorias': categorias,
        'prioridades': prioridades,
    })
def ticket_update(request, ticket_id):
    ticket = get_object_or_404(Ticket, id_compuesto=ticket_id)
    categorias = CategoriaProblema.objects.all()
    prioridades = Prioridad.objects.all()
    estados = Estado.objects.all()  

    if request.method == 'POST':
        nombre_cliente = request.POST.get('nombre_cliente')
        correo_cliente = request.POST.get('correo_cliente')
        numero_cliente = request.POST.get('numero_cliente')
        categoria_id = request.POST.get('categoria')
        prioridad_id = request.POST.get('prioridad')
        estado_id = request.POST.get('estado')  # El estado solo se puede cambiar aquí
        detalle = request.POST.get('detalle')
        imagen = request.FILES.get('imagen')

        try:
            # nombre del cliente no esté vacío
            if not nombre_cliente:
                messages.error(request, "El nombre del cliente no puede estar vacío.")
                return redirect('ticket_update', ticket_id=ticket.id_compuesto)

            # Si el cliente ya existe, lo actualizas, si no, lo crea la cochinada
            cliente, created = Cliente.objects.get_or_create(
                nombre=nombre_cliente,
                defaults={'email': correo_cliente, 'telefono': numero_cliente}
            )

            # Asignar o actualizar los datos del ticket claro que si 
            ticket.cliente = cliente
            ticket.categoria = CategoriaProblema.objects.get(id=categoria_id)
            ticket.prioridad = Prioridad.objects.get(id=prioridad_id)
            ticket.estado = Estado.objects.get(id=estado_id)  # Actualizar estado al fin ptm
            ticket.detalle = detalle
            ticket.imagen = imagen

            # Guarda los cambios del ticket
            ticket.save()

            # Si hay imagen nueva
            if imagen:
                imagen_obj = Imagen(ticket=ticket, imagen=imagen)
                imagen_obj.save()

            messages.success(request, f"Ticket {ticket.id_compuesto} actualizado.")
            return redirect('ticket_list')

        except Exception as e:
            messages.error(request, f"Error al actualizar el ticket: {e}")
            return redirect('ticket_update', ticket_id=ticket.id_compuesto)
    
    
    return render(request, 'ticket_form.html', {
        'ticket': ticket,
        'categorias': categorias,
        'prioridades': prioridades,
        'estados': estados,  # Pasar los estados al contexto
    })


def ticket_delete(request, id_compuesto):
    ticket = get_object_or_404(Ticket, id_compuesto=id_compuesto)
    if request.method == 'POST':
        ticket.delete()
        return redirect('ticket_list')  # Redirige a la lista de tickets después de eliminar
    return render(request, 'confirmar_eliminacion.html', {'ticket': ticket})

def ticket_view(request, ticket_id):
    # Obtener el ticket utilizando 'id_compuesto' como clave primaria
    ticket = get_object_or_404(Ticket, id_compuesto=ticket_id)

    # Pasar el ticket al contexto de la plantilla
    return render(request, 'ticket_view.html', {'ticket': ticket})