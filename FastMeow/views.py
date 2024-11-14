from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Cliente, Ticket, Estado, CategoriaProblema, Prioridad
from django.core.exceptions import ValidationError


def menu(request):
    return render(request, 'menu_principal.html')

def abrirticket(request):
    # Obtener los datos de clientes y productos para el formulario
    categoria = CategoriaProblema.objects.all()
    prioridad= Prioridad.objects.all()
    return render(request, 'abrirticket.html', {'categoria': categoria, 'prioridad': prioridad})

def status(request):
    return render(request, 'status.html')

def guardar_ticket(request):
    # Obtener los estados, categorías y prioridades
    categorias = CategoriaProblema.objects.all()
    prioridades = Prioridad.objects.all()

    # Si el formulario se ha enviado
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_cliente = request.POST.get('nombre_cliente')
        correo_cliente = request.POST.get('correo_cliente')
        numero_cliente = request.POST.get('numero_cliente')
        categoria_id = request.POST.get('categoria')
        prioridad_id = request.POST.get('prioridad')
        detalle = request.POST.get('detalle')
        imagen = request.FILES.get('imagen')

        # Crear o obtener el cliente
        cliente, created = Cliente.objects.get_or_create(
            nombre=nombre_cliente,
            email=correo_cliente,
            telefono=numero_cliente
        )

        # Asignar estado "En espera"
        estado = Estado.objects.get(nombre="En espera")

        # Crear el ticket
        categoria = CategoriaProblema.objects.get(id=categoria_id)
        prioridad = Prioridad.objects.get(id=prioridad_id)

        ticket = Ticket(
            cliente=cliente,
            categoria=categoria,
            estado=estado,
            prioridad=prioridad,
            detalle=detalle,
            imagen=imagen
        )
        ticket.save()

        # Redirigir al usuario a la página de estatus o donde desees
        return redirect('status')

    # Si no se ha enviado el formulario, renderizar el formulario en blanco
    return render(request, 'abrir_ticket.html', {
        'categorias': categorias,
        'prioridades': prioridades
    })

