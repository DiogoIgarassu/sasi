from django.db import models

# Create your models here.
class Escolaridade(models.Model):
    nivel = models.CharField(max_length=100)

    def __str__(self):
        return self.nivel

class Status(models.Model):
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.status


class Curso(models.Model):
    curso = models.CharField(max_length=200)

    def __str__(self):
        return self.curso


class UnidadeSuas(models.Model):
    unidade = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.unidade


class Bairro(models.Model):
    bairro = models.CharField(max_length=100)

    def __str__(self):
        return self.bairro


class Localidade(models.Model):
    bairro = models.ForeignKey(Bairro, on_delete=models.CASCADE)
    localidade = models.CharField(max_length=100)

    def __str__(self):
        return self.localidade