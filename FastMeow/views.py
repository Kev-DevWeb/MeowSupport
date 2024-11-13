from django.shortcuts import render


def menu(request):
    return render(request, 'menu_principal.html')

def abrirticket(request):
    return render(request, 'abrirticket.html')

def status(request):
    return render(request, 'status.html')

