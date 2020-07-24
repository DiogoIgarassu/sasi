from django.db import models
from django.conf import settings
from django.db.models import CASCADE

class teste(models.Model):
    data = models.DateTimeField('Cadastrado em', auto_now_add=True)

class Usuario(models.Model):
    created_at = models.DateTimeField('Cadastrado em', auto_now_add=True)
    update_at = models.DateTimeField('Atualizado em', auto_now=True)
    CPF = models.CharField(max_length=11, unique=True)
    NIS = models.CharField(max_length=11, blank=True)
    RG = models.CharField(max_length=11, blank=True)
    nome = models.CharField(max_length=80)
    nascimento = models.DateField(null=True, blank=True)
    nome_mae = models.CharField(max_length=80)
    endereco = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    referencia = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=50)
    telefone1 = models.CharField(max_length=9, blank=True)
    telefone2 = models.CharField(max_length=9, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='inclusao_usuario', default=None)
    STATUS = (
        ('ON', 'Ativo'),
        ('OFF', 'Inativo'),
    )
    image = models.ImageField(
        upload_to='usuarios/images', verbose_name='Foto',
        null=True, blank=True
    )
    status = models.CharField(max_length=3, choices=STATUS)

    def __str__(self):
        return self.nome


class Beneficio(models.Model):
    nome_beneficio = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='inclusao_beneficio', default=None)
    descricao = models.TextField(null=True, blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    update_at = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return self.nome_beneficio


class Estoque_beneficio(models.Model):
    tipo_beneficio = models.ForeignKey(Beneficio, on_delete=CASCADE, related_name='estoque')
    quantidade = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='inclusao_estoque', default=None)
    observacao = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    update_at = models.DateTimeField('Atualizado em', auto_now=True)

    def __str__(self):
        return self.quantidade


class Beneficiario(models.Model):
    created_at = models.DateTimeField('Incluído em', auto_now_add=True)
    update_at = models.DateTimeField('Atualizado em', auto_now=True)
    nome = models.ForeignKey(Usuario, on_delete=CASCADE, related_name='nome_beneficiario')
    tipo_beneficio = models.ForeignKey(Beneficio, on_delete=CASCADE, related_name='tipo_beneficio')
    qtd_familia = models.CharField(max_length=3, blank=True)
    renda = models.CharField(max_length=7, blank=True)
    equipamento = models.CharField(max_length=20, blank=True)
    parecer = models.TextField(null=True, blank=True)
    assistente_social = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='inclusao_beneficiario', default=None)
    data_beneficio = models.DateField(null=True, blank=True)
    situacao = models.CharField(max_length=20, blank=True)
    image = models.ImageField(
        upload_to='Usuarios/beneficios', verbose_name='Foto',
        null=True, blank=True
    )

    def __str__(self):
        return str(self.nome)
