# Generated by Django 3.0.8 on 2020-07-19 23:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Beneficio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_beneficio', models.CharField(max_length=30)),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='inclusao_beneficio', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='teste',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now_add=True, verbose_name='Cadastrado em')),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Cadastrado em')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('CPF', models.CharField(max_length=11, unique=True)),
                ('NIS', models.CharField(blank=True, max_length=11, unique=True)),
                ('RG', models.CharField(blank=True, max_length=11)),
                ('nome', models.CharField(max_length=80)),
                ('nascimento', models.DateField(blank=True, null=True)),
                ('nome_mae', models.CharField(max_length=80)),
                ('endereco', models.CharField(max_length=100)),
                ('bairro', models.CharField(max_length=100)),
                ('referencia', models.CharField(blank=True, max_length=100)),
                ('cidade', models.CharField(max_length=50)),
                ('telefone1', models.CharField(blank=True, max_length=9)),
                ('telefone2', models.CharField(blank=True, max_length=9)),
                ('observacoes', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='Usuarios/fotos', verbose_name='Foto')),
                ('status', models.CharField(choices=[('ON', 'Ativo'), ('OFF', 'Inativo')], max_length=3)),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='inclusao_usuario', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Estoque_beneficio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.CharField(max_length=10)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('tipo_beneficio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='estoque', to='Usuarios.Beneficio')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='inclusao_estoque', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Beneficiario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Incluído em')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('qtd_familia', models.CharField(blank=True, max_length=3)),
                ('parecer', models.TextField(blank=True, null=True)),
                ('assistente_social', models.CharField(blank=True, max_length=50)),
                ('data_beneficio', models.DateField(auto_now=True, verbose_name='Data')),
                ('image', models.ImageField(blank=True, null=True, upload_to='Usuarios/beneficios', verbose_name='Foto')),
                ('CPF', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='CPF_beneficiario', to='Usuarios.Usuario')),
                ('tipo_beneficio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tipo_beneficio', to='Usuarios.Beneficio')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='inclusao_beneficiario', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
