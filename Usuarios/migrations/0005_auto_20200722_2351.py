# Generated by Django 3.0.8 on 2020-07-23 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0004_auto_20200722_2258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios/images', verbose_name='Foto'),
        ),
    ]