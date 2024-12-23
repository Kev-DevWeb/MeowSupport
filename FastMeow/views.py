from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Cliente, Ticket, Estado, CategoriaProblema, Prioridad, Imagen, TicketsArchivados, Comentario
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.db import transaction


def menu(request):
    return render(request, 'menu_principal.html')

def abrirticket(request):
    # Obtener los datos de clientes y productos para el formulario
    categoria = CategoriaProblema.objects.all()
    prioridad = Prioridad.objects.all()
    
    today = timezone.now().date()  # Obtener la fecha de hoy
    
    return render(request, 'abrirticket.html', {'categoria': categoria, 'prioridad': prioridad, 'today': today})

def guardar_ticket(request):
    categorias = CategoriaProblema.objects.all()
    prioridades = Prioridad.objects.all()

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
                fecha_creacion=fecha_creacion  # Asignar la fecha
            )
            ticket.save()

            if imagen:
                imagen_obj = Imagen(
                    ticket=ticket,
                    imagen=imagen
                )
                imagen_obj.save()

            # Mensaje de éxito
            messages.success(request, f"Ticket creado para {nombre_cliente} con ID {ticket.id_compuesto}")
            return redirect('abrir_ticket')
        except Exception as e:
            # Mensaje de error
            messages.error(request, f"No se pudo registrar el ticket. Error: {e}")
            return redirect('abrir_ticket')


def status(request):
    return render(request, 'status.html')


def buscar_status_por_id_compuesto(request):
    # Obtenemos el 'ticket_id' desde los parámetros GET de la URL
    ticket_id = request.GET.get('ticket_id')  # Esto obtiene el ticket_id enviado a través de la URL
    
    status = None
    imagen = None
    comentarios = None

    # Verificamos si ticket_id está presente antes de intentar buscar el ticket
    if ticket_id:
        try:
            # Usamos el ticket_id para buscar el ticket correspondiente
            status = Ticket.objects.get(id_compuesto=ticket_id)
            # Usamos filter() para obtener todas las imágenes y comentarios relacionados
            imagen = Imagen.objects.filter(ticket=status).first()  # Obtener la primera imagen si existe
            comentarios = Comentario.objects.filter(ticket=status)  # Obtener todos los comentarios
        except Ticket.DoesNotExist:
            status = None

    return render(request, 'status.html', {
        'status': status,
        'id_compuesto': ticket_id,  # Pasamos el ticket_id a la plantilla para mostrarlo
        'imagen': imagen,  # Puede ser None si no se encuentra imagen
        'comentarios': comentarios  # Puede ser un QuerySet vacío si no hay comentarios
    })


def agregar_comentario_cliente(request, ticket_id):
    # Obtener el ticket por su id_compuesto
    ticket = get_object_or_404(Ticket, id_compuesto=ticket_id)
    
    # Obtener todos los comentarios asociados al ticket
    comentarios = Comentario.objects.filter(ticket=ticket).all()

    if request.method == 'POST':
        comentario_texto = request.POST.get('comentarios')  # Asegurarse de usar el nombre correcto del campo

        if comentario_texto:
            # Obtener el nombre del cliente desde el ticket
            nombre_cliente = ticket.cliente.nombre
            
            # Crear el nuevo comentario
            comentario = Comentario(
                ticket=ticket,
                tecnico=nombre_cliente,  # Guardar el nombre del cliente como nombre del técnico
                comentario=comentario_texto
            )
            comentario.save()

            # Redirige a la página de detalles del ticket con los datos adecuados
            return redirect('status')

    # Si no se hace POST, se pasa todo al contexto de la plantilla
    return render(request, 'status.html')



#====================================Administradores y tecnicos ===========================

def menu2(request, rol, clave, nombre):

    # Validar los parámetros: rol, clave y nombre
    if not nombre:
        return HttpResponse("Acceso denegado: Falta el nombre.", status=403)

    if not ((rol == "administrador" and clave == "admin123") or 
            (rol == "tecnico" and clave == "tecnico123")):
        # Si no se cumple la validación, denegar acceso
        return HttpResponse("Acceso denegado: Rol o clave incorrectos.", status=403)

    # Obtener todos los tickets
    query = Ticket.objects.all()

    # Aplicar filtros dinámicos
    cliente_id = request.GET.get('cliente', '')
    categoria_id = request.GET.get('categoria', '')
    estado_id = request.GET.get('estado', '')
    prioridad_id = request.GET.get('prioridad', '')

    if cliente_id:
        query = query.filter(cliente_id=cliente_id)
    if categoria_id:
        query = query.filter(categoria_id=categoria_id)
    if estado_id:
        query = query.filter(estado_id=estado_id)
    if prioridad_id:
        query = query.filter(prioridad_id=prioridad_id)

    # Obtener la imagen relacionada con cada ticket desde la tabla Imagen
    for ticket in query:
        # Buscar la primera imagen asociada al ticket
        imagen = Imagen.objects.filter(ticket=ticket).first()
        ticket.imagen_url = imagen.imagen.url if imagen else None

    # Obtener datos adicionales para los filtros
    clientes = Cliente.objects.all()
    categorias = CategoriaProblema.objects.all()
    estados = Estado.objects.all()
    prioridades = Prioridad.objects.all()
    tickets_archivados = TicketsArchivados.objects.all()

    # Renderizar la plantilla con los datos
    return render(request, 'menu2.html', {
        'tickets': query,
        'clientes': clientes,
        'categorias': categorias,
        'estados': estados,
        'prioridades': prioridades,
        'tickets_archivados': tickets_archivados,
        'nombre': nombre,
        'rol': rol,  # Pasa el rol
        'clave': clave,  # Pasa la clave
    })



def ver(request, ticket_id, rol, clave, nombre):
    # Obtener el ticket utilizando 'id_compuesto' como clave primaria
    ticket = get_object_or_404(Ticket, id_compuesto=ticket_id)

    # Buscar la primera imagen asociada al ticket
    imagen = Imagen.objects.filter(ticket=ticket).first()

    # Obtener todos los comentarios asociados al ticket
    comentarios = Comentario.objects.filter(ticket=ticket).all()

    # Obtener las listas de prioridades, estados y categorías
    priority = Prioridad.objects.all()
    status = Estado.objects.all()
    categorias = CategoriaProblema.objects.all()

    # Si el formulario se envía con POST, actualizar el estado y categoría
    if request.method == 'POST':
        # Obtener los valores de estado y categoría desde el formulario
        nuevo_estado = request.POST.get('Estado')
        nueva_prioridad = request.POST.get('prioridad')

        if nuevo_estado and nueva_prioridad:
            try:
                # Actualizar el estado y la categoría del ticket
                ticket.estado_id = nuevo_estado
                ticket.prioridad_id = nueva_prioridad
                ticket.save()

                # Redirigir a la misma vista con los cambios reflejados
                return redirect('ver', ticket_id=ticket.id_compuesto, rol=rol, clave=clave, nombre=nombre)
            except (Estado.DoesNotExist, CategoriaProblema.DoesNotExist):
                # Si el estado o la categoría no existen
                error_message = "Estado o categoría no válidos"
        else:
            error_message = "El estado y la categoría son obligatorios."

    # Pasar el ticket, la imagen, los comentarios, y las variables al contexto de la plantilla
    return render(request, 'ver.html', {
        'ticket': ticket,
        'rol': rol,
        'clave': clave,
        'nombre': nombre,
        'priority': priority,
        'status': status,
        'imagen': imagen.imagen.url if imagen else None,
        'comentarios': comentarios,
        'categorias': categorias,
        'error_message': error_message if 'error_message' in locals() else None  # Mostrar mensaje de error si existe
    })


def agregar_comentario(request, ticket_id, rol, clave, nombre):
    ticket = get_object_or_404(Ticket, id_compuesto=ticket_id)  # Obtener el ticket por su id_compuesto
    
    # Obtener todos los comentarios asociados al ticket
    comentarios = Comentario.objects.filter(ticket=ticket).all()
    # Buscar la primera imagen asociada al ticket
    imagen = Imagen.objects.filter(ticket=ticket).first()
    # Obtener las listas de prioridades y estados
    priority = Prioridad.objects.all()
    status = Estado.objects.all()

    if request.method == 'POST':
        comentario_texto = request.POST.get('comentarios')  # Asegurarse de usar el nombre correcto del campo

        if comentario_texto:
            # Crear el nuevo comentario
            comentario = Comentario(
                ticket=ticket, 
                tecnico=nombre,  # Guardar el nombre del técnico
                comentario=comentario_texto
            )
            comentario.save()

            # Redirige a la página de detalles del ticket
            return redirect('ver', ticket_id=ticket_id, rol=rol, clave=clave, nombre=nombre)

    # Si no se hace POST, se pasa todo al contexto de la plantilla
    return render(request, 'ver.html', {
        'ticket': ticket,
        'rol': rol,
        'clave': clave,
        'nombre': nombre,
        'priority': priority,
        'status': status,
        'imagen': imagen.imagen.url if imagen else None,  # Pasar la URL de la imagen si existe
        'comentarios': comentarios,  # Pasar los comentarios al contexto
    })

def editar(request, ticket_id, rol, clave, nombre):
    categorias = CategoriaProblema.objects.all()
    prioridades = Prioridad.objects.all()
    clientes = Cliente.objects.all()
    estados = Estado.objects.all()  # Asegúrate de obtener todos los estados
    ticket = Ticket.objects.get(id_compuesto=ticket_id)  # Obtener el ticket actual por su ID
    status = ticket.estado  # Obtener el estado actual del ticket

    # Obtener la primera imagen asociada al ticket si existe
    imagen = ticket.imagenes.first()  # Usamos 'imagenes' en lugar de 'imagen_set'

    if request.method == 'POST':
        # Obtener los datos del formulario
        cliente_id = request.POST.get('cliente')
        categoria_id = request.POST.get('categoria')
        prioridad_id = request.POST.get('prioridad')
        estado_id = request.POST.get('estado')
        detalle = request.POST.get('detalle')
        imagen_archivo = request.FILES.get('imagen')  # Imagen subida

        try:
            # Actualizar el ticket con los nuevos datos
            cliente = Cliente.objects.get(id=cliente_id)
            estado = Estado.objects.get(id=estado_id)
            categoria = CategoriaProblema.objects.get(id=categoria_id)
            prioridad = Prioridad.objects.get(id=prioridad_id)

            # Asignar nuevos valores al ticket
            ticket.cliente = cliente
            ticket.categoria = categoria
            ticket.estado = estado
            ticket.prioridad = prioridad
            ticket.detalle = detalle

            ticket.save()  # Guardar los cambios

            # Si se ha subido una nueva imagen, actualizamos la imagen relacionada
            if imagen_archivo:
                # Si ya existe una imagen anterior, la eliminamos
                if ticket.imagenes.exists():  # Usar 'imagenes' en lugar de 'imagen_set'
                    ticket.imagenes.all().delete()

                # Crear un nuevo objeto de Imagen
                imagen_obj = Imagen(ticket=ticket, imagen=imagen_archivo)
                imagen_obj.save()

            # Mensaje de éxito
            messages.success(request, f"Ticket {ticket.id_compuesto} actualizado con éxito.")
            return redirect('editar', ticket_id=ticket.id, rol=rol, clave=clave, nombre=nombre)

        except Exception as e:
            # Mensaje de error
            messages.error(request, f"No se pudo actualizar el ticket. Error: {e}")
            return render(request, 'editar.html', {
                'ticket': ticket,
                'rol': rol,
                'clave': clave,
                'nombre': nombre,
                'prioridades': prioridades,
                'status': status,
                'categorias': categorias,
                'clientes': clientes,
                'estados': estados,  # Pasar la lista de estados
                'imagen': imagen.imagen.url if imagen else None  # Verificar si imagen existe
            })

    
    # Si la solicitud es GET, se muestra el formulario con los datos actuales
    return render(request, 'editar.html', {
        'ticket': ticket,
        'rol': rol,
        'clave': clave,
        'nombre': nombre,
        'categorias': categorias,
        'prioridades': prioridades,
        'clientes': clientes,
        'status': status,
        'estados': estados,  # Pasar la lista de estados
    })


from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.http import HttpResponse

def eliminar(request, ticket_id, rol, clave, nombre):
    ticket = get_object_or_404(Ticket, id_compuesto=ticket_id)

    if request.method == 'POST':
        with transaction.atomic():
            # Crear un registro en TicketsArchivados con los datos del ticket actual
            ticket_archivado = TicketsArchivados.objects.create(
                cliente=ticket.cliente,
                categoria=ticket.categoria,
                estado=ticket.estado,
                prioridad=ticket.prioridad,
                fecha_creacion=ticket.fecha_creacion,
                detalle=ticket.detalle,
                id_compuesto=ticket.id_compuesto,
            )
            
            # Mover comentarios e imágenes asociadas
            Comentario.objects.filter(ticket=ticket).update(ticket=None, ticket_archivado=ticket_archivado)
            Imagen.objects.filter(ticket=ticket).update(ticket=None, ticket_archivado=ticket_archivado)
            
            # Eliminar el ticket original
            ticket.delete()

        return redirect('menu2', rol=rol, clave=clave, nombre=nombre)

    return HttpResponse("Método no permitido", status=405)


def nuevoticket(request, rol, clave, nombre):
    # Obtener los datos de clientes y productos para el formulario
    categoria = CategoriaProblema.objects.all()
    prioridad = Prioridad.objects.all()
    
    today = timezone.now().date()  # Obtener la fecha de hoy
    
    return render(request, 'nuevoticket.html', {'categoria': categoria, 'prioridad': prioridad, 'today': today, 'nombre': nombre,
        'rol': rol, 
        'clave': clave, })

def guardar_ticket2(request, rol, clave, nombre):
    categorias = CategoriaProblema.objects.all()
    prioridades = Prioridad.objects.all()

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
                fecha_creacion=fecha_creacion  # Asignar la fecha
            )
            ticket.save()

            if imagen:
                imagen_obj = Imagen(
                    ticket=ticket,
                    imagen=imagen
                )
                imagen_obj.save()

            # Mensaje de éxito
            messages.success(request, f"Ticket creado para {nombre_cliente} con ID {ticket.id_compuesto}")
            return redirect('nuevoticket', rol=rol, clave=clave, nombre=nombre)
        except Exception as e:
            # Mensaje de error
            messages.error(request, f"No se pudo registrar el ticket. Error: {e}")
            return redirect('nuevoticket', rol=rol, clave=clave, nombre=nombre)
        
def ver_archivados(request, ticket_id2, rol, clave, nombre):
    # Obtener el ticket archivado utilizando 'id_compuesto' como clave primaria
    ticket2 = get_object_or_404(TicketsArchivados, id_compuesto=ticket_id2)  # Asegúrate de que es TicketsArchivados
    
    # Buscar la primera imagen asociada al ticket archivado
    imagen = Imagen.objects.filter(ticket_archivado=ticket2).first()

    # Obtener todos los comentarios asociados al ticket archivado
    comentarios = Comentario.objects.filter(ticket_archivado=ticket2).all()

    # Pasar el ticket, la imagen, los comentarios y las variables al contexto de la plantilla
    return render(request, 'ver_archivados.html', {
        'ticket2': ticket2,
        'rol': rol,
        'clave': clave,
        'nombre': nombre,
        'imagen': imagen.imagen.url if imagen else None,  # Verifica si hay imagen
        'comentarios': comentarios,
    })


def mis_tickets(request):
    tickets = None

    if request.method == 'POST':
        # Recogemos los datos del formulario
        nombre_cliente = request.POST.get('nombre_cliente')
        correo_cliente = request.POST.get('correo_cliente')
        numero_cliente = request.POST.get('numero_cliente')

        try:
            # Verificamos si existe el cliente con los datos proporcionados
            cliente = Cliente.objects.get(
                nombre__iexact=nombre_cliente,  # le vale que lo pongas en Mayusculas y Minusculas
                email__iexact=correo_cliente,  # le vale que lo pongas en Mayusculas y Minusculas
                telefono=numero_cliente
            )

            # con esta madre se filtra
            tickets = Ticket.objects.filter(cliente=cliente)

            if not tickets.exists():
                messages.info(request, "No se encontraron tickets asociados a tus datos.")
        except Cliente.DoesNotExist:
            messages.error(request, "No se encontró ningún ticket con los datos proporcionados.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {e}")

    # Renderizamos la página con el formulario y los resultados
    return render(request, 'mis_tickets.html', {'tickets': tickets})