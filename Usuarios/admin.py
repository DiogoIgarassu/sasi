from django.contrib import admin
from .models import Usuario, Estoque_beneficio, Beneficio, Beneficiario



class EstoqueAdmin(admin.ModelAdmin):
    list_display = ['tipo_beneficio', 'quantidade']
    search_fields = ['tipo_beneficio']
    #fields = ['title', 'sub_title']

class BeneficiariosAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo_beneficio', 'data_beneficio', 'id']
    search_fields = ['nome']

class UsuariosAdmin(admin.ModelAdmin):
    list_display = ['CPF', 'nome', 'nascimento', 'nome_mae']
    search_fields = ['CPF']

admin.site.register(Usuario, UsuariosAdmin)
admin.site.register(Beneficio)
admin.site.register(Estoque_beneficio, EstoqueAdmin)
admin.site.register(Beneficiario, BeneficiariosAdmin)

