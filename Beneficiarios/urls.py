from Beneficiarios.views import *
from django.urls import path

app_name = 'Beneficiarios'

urlpatterns = [
    path('emergencial', busca_auxlio, name='emergencial'),
    path('buscar_cestas', busca_cestas, name='busca_cestas'),
    path('registrar_cesta', beneficiario_register, name='registrar_cesta'),
    path('consulta_beneficiario/<int:pk>/', beneficiario_details, name='beneficiario_details'),
    path('promove_details/<int:pk>/', promove_details, name='promove_details'),
    path('buscar_cestas/<str:cpf>/', busca_cestas, name='busca_cestas_cpf'),
    path('lista_cestas/', lista_cestas, name='lista_cestas'),
    path('listas_promove/', promove_cursos, name='promove_cursos'),
    path('export_csv/', export_csv, name='export_csv'),
    path('export_cursos_csv/', export_cursos_csv, name='export_cursos_csv'),
    path('export_pdf/', export_pdf, name='export_pdf'),
    path('export_cursos_pdf/', export_cursos_pdf, name='export_cursos_pdf'),
    path('relatorios/', relatorios, name='relatorios'),

]
