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
from FastMeow.views import abrirticket, menu, status, guardar_ticket

urlpatterns = [
    path('', menu, name='menu'),  
    path('admin/', admin.site.urls), 
    path('status/', status, name='status'),  
    path('abrirticket/', abrirticket, name='abrir_ticket'), 
    path('guardar_ticket/', guardar_ticket, name='guardar_ticket'), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
