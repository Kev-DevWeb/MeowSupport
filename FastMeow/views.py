from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Cliente, Ticket, Estado, CategoriaProblema, Prioridad, Imagen
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

def menu(request):
    return render(request, 'menu_principal.html')

def status(request):
    return render(request, 'status.html')



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
            messages.success(request, f"Ticket creado para {nombre_cliente} con ID {ticket.id}")
            return redirect('abrir_ticket')
        except Exception as e:
            # Mensaje de error
            messages.error(request, f"No se pudo registrar el ticket. Error: {e}")
            return redirect('abrir_ticket')

        
