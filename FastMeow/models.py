from django.db import models
from django.utils import timezone
import re

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
    id_compuesto = models.CharField(max_length=255, unique=True, blank=True)  # Campo id_compuesto
    
    def save(self, *args, **kwargs):
        if not self.id_compuesto:  # Si no existe un id_compuesto, generarlo
            # Obtener las iniciales y la fecha
            inicial_cliente = self.cliente.nombre[0].upper()
            inicial_categoria = self.categoria.nombre[0].upper() if self.categoria else ''
            inicial_prioridad = self.prioridad.nombre[0].upper() if self.prioridad else ''
            fecha = self.fecha_creacion.strftime('%Y%m%d')  # Formato YYYYMMDD
            
            # Buscar el último ticket con la misma fecha
            ultimo_ticket = Ticket.objects.filter(id_compuesto__startswith=f"{inicial_cliente}{inicial_categoria}{inicial_prioridad}{fecha}").order_by('-id_compuesto').first()
            
            if ultimo_ticket:
                # Extraer el contador y sumarle 1
                match = re.search(r'-(\d+)$', ultimo_ticket.id_compuesto)
                if match:
                    contador = int(match.group(1)) + 1
                else:
                    contador = 1
            else:
                contador = 1

            # Generar el nuevo id_compuesto
            self.id_compuesto = f"{inicial_cliente}{inicial_categoria}{inicial_prioridad}{fecha}-{contador}"

        super().save(*args, **kwargs)  # Llamar al método save original

    def delete(self, *args, **kwargs):
        # Copiar el ticket a TicketsArchivados
        archived_ticket = TicketsArchivados.objects.create(
            cliente=self.cliente,
            categoria=self.categoria,
            estado=self.estado,
            prioridad=self.prioridad,
            fecha_creacion=self.fecha_creacion,
            detalle=self.detalle,
            numero=self.numero,
            id_compuesto=self.id_compuesto
        )

        # Copiar los comentarios e imágenes a los tickets archivados
        for comentario in self.comentarios.all():
            Comentario.objects.create(
                ticket_archivado=archived_ticket,
                tecnico=comentario.tecnico,
                comentario=comentario.comentario,
                estado=comentario.estado,
                prioridad=comentario.prioridad
            )

        for imagen in self.imagenes.all():
            Imagen.objects.create(
                ticket_archivado=archived_ticket,
                imagen=imagen.imagen,
                descripcion=imagen.descripcion
            )

        # Eliminar el ticket original
        super(Ticket, self).delete(*args, **kwargs)

    def __str__(self):
        return f"Ticket #{self.id_compuesto}"

class Comentario(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, related_name='comentarios')
    ticket_archivado = models.ForeignKey('TicketsArchivados', on_delete=models.SET_NULL, null=True, related_name='comentarios_archivados')
    tecnico = models.CharField(max_length=100)
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    prioridad = models.ForeignKey(Prioridad, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Comentario por {self.tecnico} en Ticket {self.ticket.id_compuesto}"

class Imagen(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, related_name='imagenes')
    ticket_archivado = models.ForeignKey('TicketsArchivados', on_delete=models.SET_NULL, null=True, related_name='imagenes_archivadas')
    imagen = models.ImageField(upload_to='ticket_images/')

    def __str__(self):
        return f"Imagen para Ticket {self.ticket.id_compuesto}"

class TicketsArchivados(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaProblema, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    prioridad = models.ForeignKey(Prioridad, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    detalle = models.TextField()
    numero = models.IntegerField()
    id_compuesto = models.CharField(max_length=50, unique=True, editable=False)

    def __str__(self):
        return f"Ticket Archivado #{self.id_compuesto}"
