from Usuarios.views import *
from django.urls import path

app_name = 'Usuarios'

urlpatterns = [
    path('', buscar_usuarios, name='index'),
    path('todos_usuarios', all_usuarios, name='all_usuarios'),
    path('Cadastrar/', add_usuarios, name='cadastrar'),
    path('delete/<int:pk>/', del_usuario, name='url_delete'),
    path('update/<int:pk>/', up_usuario, name='url_update'),
    path('beneficiario/', beneficiario, name='beneficiario'),
    path('busca_beneficiario', buscar_beneficiarios, name='busca_beneficiarios'),
    path('todos_beneficios', all_beneficiarios, name='all_beneficiarios'),
    path('incluir_beneficio/<str:cpf>/', add_beneficiario, name='incluir_beneficio'),
    path('update_beneficiario/<int:pk>/', up_beneficiario, name='update_beneficiario'),
    path('upload_dados/', upload_dados, name='upload_dados'),
]
