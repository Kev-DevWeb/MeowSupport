from django.shortcuts import render, redirect

# Create your views here.
def abrirticket (request):
    return render(request, "abrirticket.html")

