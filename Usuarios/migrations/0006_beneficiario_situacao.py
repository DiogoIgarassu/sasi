# Generated by Django 3.0.8 on 2020-07-24 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0005_auto_20200722_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='beneficiario',
            name='situacao',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]