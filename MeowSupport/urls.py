"""
URL configuration for MeowSupport project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from FastMeow.views import abrirticket, menu, status, guardar_ticket, buscar_status_por_id_compuesto, menu2, ver, agregar_comentario, editar, eliminar, nuevoticket, guardar_ticket2, ver_archivados

urlpatterns = [
    path('', menu, name='menu'),  
    path('admin/', admin.site.urls), 
    path('status/', status, name='status'),  
    path('abrirticket/', abrirticket, name='abrir_ticket'), 
    path('guardar_ticket/', guardar_ticket, name='guardar_ticket'), 
    path('buscar_status/', buscar_status_por_id_compuesto, name='buscar_status_por_id_compuesto'),
    path('menu2/<str:rol>/<str:clave>/<str:nombre>/', menu2, name='menu2'),
    path('ver/<str:ticket_id>/<str:rol>/<str:clave>/<str:nombre>/', ver, name='ver'),
    path('ticket/<str:ticket_id>/agregar_comentario/<str:rol>/<str:clave>/<str:nombre>/', agregar_comentario, name='agregar_comentario'),
    path('editar/<str:ticket_id>/<str:rol>/<str:clave>/<str:nombre>/', editar, name='editar'),
    path('eliminar/<str:ticket_id>/<str:rol>/<str:clave>/<str:nombre>/', eliminar, name='eliminar'),
    path('nuevoticket/<str:rol>/<str:clave>/<str:nombre>/', nuevoticket, name='nuevoticket'),
    path('guardar_ticket2/<str:rol>/<str:clave>/<str:nombre>/', guardar_ticket2, name='guardar_ticket2'),
    path('ver_archivados/<str:ticket_id2>/<str:rol>/<str:clave>/<str:nombre>/', ver_archivados, name='ver_archivados'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



