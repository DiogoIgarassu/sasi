# Generated by Django 3.0.8 on 2020-07-23 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0003_auto_20200721_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiario',
            name='equipamento',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='NIS',
            field=models.CharField(blank=True, max_length=11),
        ),
    ]