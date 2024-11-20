from django.db import models
from django.utils import timezone
import re

# Modelos principales
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nombre


class CategoriaProblema(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Prioridad(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Ticket(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaProblema, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    prioridad = models.ForeignKey(Prioridad, on_delete=models.SET_NULL, null=True)
    detalle = models.TextField()
    fecha_creacion = models.DateTimeField(default=timezone.now)
    id_compuesto = models.CharField(max_length=255, primary_key=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id_compuesto:  # Si no existe un id_compuesto, generarlo
            inicial_cliente = self.cliente.nombre[0].upper()
            inicial_categoria = self.categoria.nombre[0].upper() if self.categoria else ''
            inicial_prioridad = self.prioridad.nombre[0].upper() if self.prioridad else ''
            fecha = self.fecha_creacion.strftime('%Y%m%d')  # Formato YYYYMMDD

            ultimo_ticket = Ticket.objects.filter(
                id_compuesto__startswith=f"{inicial_cliente}{inicial_categoria}{inicial_prioridad}{fecha}"
            ).order_by('-id_compuesto').first()

            if ultimo_ticket:
                match = re.search(r'-(\d+)$', ultimo_ticket.id_compuesto)
                contador = int(match.group(1)) + 1 if match else 1
            else:
                contador = 1

            self.id_compuesto = f"{inicial_cliente}{inicial_categoria}{inicial_prioridad}{fecha}-{contador}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket #{self.id_compuesto}"


class Comentario(models.Model):
    ticket = models.ForeignKey(Ticket, to_field='id_compuesto', on_delete=models.SET_NULL, null=True, related_name='comentarios')
    ticket_archivado = models.ForeignKey('TicketsArchivados', on_delete=models.SET_NULL, null=True, related_name='comentarios_archivados')
    tecnico = models.CharField(max_length=100)
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.ticket:
            return f"Comentario por {self.tecnico} en Ticket {self.ticket.id_compuesto}"
        elif self.ticket_archivado:
            return f"Comentario por {self.tecnico} en Ticket Archivado {self.ticket_archivado.id_compuesto}"
        return "Comentario sin ticket asociado"

class Imagen(models.Model):
    ticket = models.ForeignKey(Ticket, to_field='id_compuesto', on_delete=models.SET_NULL, null=True, related_name='imagenes')
    ticket_archivado = models.ForeignKey('TicketsArchivados', on_delete=models.SET_NULL, null=True, related_name='imagenes_archivadas')
    imagen = models.ImageField(upload_to='ticket_images/')

    def __str__(self):
        if self.ticket:
            return f"Imagen para Ticket {self.ticket.id_compuesto}"
        elif self.ticket_archivado:
            return f"Imagen para Ticket Archivado {self.ticket_archivado.id_compuesto}"
        return "Imagen sin ticket asociado"
    
class TicketsArchivados(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaProblema, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    prioridad = models.ForeignKey(Prioridad, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField()
    detalle = models.TextField()
    id_compuesto = models.CharField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return f"Ticket Archivado #{self.id_compuesto}"


