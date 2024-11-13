from django.db import models

# Create your models here.


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

    def __str__(self):
        return f"Ticket #{self.id_compuesto}"

class Comentario(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comentarios')
    tecnico = models.CharField(max_length=100)  # O podrías tener un modelo 'Tecnico' y usar una ForeignKey aquí
    comentario = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True)
    prioridad = models.ForeignKey(Prioridad, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Comentario por {self.tecnico} en Ticket {self.ticket.id_compuesto}"

class Imagen(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='ticket_images/')
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagen para Ticket {self.ticket.id_compuesto}"
