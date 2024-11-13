from django.db import models

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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    detalle = models.TextField()
    numero = models.IntegerField()
    id_compuesto = models.CharField(max_length=50, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.id_compuesto:
            fecha_str = self.fecha_creacion.strftime('%Y%m%d')
            self.id_compuesto = f"{self.cliente.nombre[:3].upper()}-{self.categoria.nombre[:3].upper()}-{fecha_str}-{self.numero:04d}"
        super(Ticket, self).save(*args, **kwargs)

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
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

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
