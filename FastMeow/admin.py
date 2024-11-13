from django.contrib import admin
from .models import Cliente, CategoriaProblema, Estado, Prioridad, Ticket, Comentario, Imagen, TicketsArchivados
# Register your models here.

admin.site.register(Cliente)
admin.site.register(CategoriaProblema)
admin.site.register(Estado)
admin.site.register(Prioridad)
admin.site.register(Ticket)
admin.site.register(Comentario)
admin.site.register(Imagen)
admin.site.register(TicketsArchivados)