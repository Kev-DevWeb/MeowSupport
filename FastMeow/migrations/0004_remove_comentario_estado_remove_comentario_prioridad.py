# Generated by Django 5.1.1 on 2024-11-20 20:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FastMeow', '0003_comentario_ticket_archivado_imagen_ticket_archivado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comentario',
            name='estado',
        ),
        migrations.RemoveField(
            model_name='comentario',
            name='prioridad',
        ),
    ]