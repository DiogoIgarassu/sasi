from django.forms import ModelForm
from django import forms
from .models import Usuario, Beneficiario
import io
import csv


class user_form(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['CPF', 'NIS', 'RG', 'nome', 'nascimento', 'nome_mae', 'endereco', 'bairro', 'referencia', 'cidade',
                  'telefone1', 'telefone2', 'observacoes', 'image', 'status']

class beneficiario_form(forms.ModelForm):
    class Meta:
        model = Beneficiario
        fields = ['qtd_familia', 'renda', 'parecer', 'assistente_social', 'data_beneficio', 'image']

