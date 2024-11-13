# Generated by Django 5.1.3 on 2024-11-13 03:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaProblema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('telefono', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Prioridad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('detalle', models.TextField()),
                ('numero', models.IntegerField()),
                ('id_compuesto', models.CharField(editable=False, max_length=50, unique=True)),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='FastMeow.categoriaproblema')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FastMeow.cliente')),
                ('estado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='FastMeow.estado')),
                ('prioridad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='FastMeow.prioridad')),
            ],
        ),
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='ticket_images/')),
                ('descripcion', models.CharField(blank=True, max_length=255)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='FastMeow.ticket')),
            ],
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tecnico', models.CharField(max_length=100)),
                ('comentario', models.TextField()),
                ('fecha_comentario', models.DateTimeField(auto_now_add=True)),
                ('estado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='FastMeow.estado')),
                ('prioridad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='FastMeow.prioridad')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='FastMeow.ticket')),
            ],
        ),
    ]
