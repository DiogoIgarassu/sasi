from Beneficiarios.views import *
from django.urls import path

app_name = 'Beneficiarios'

urlpatterns = [
    path('emergencial', busca_auxlio, name='emergencial'),
    path('buscar_cestas', busca_cestas, name='busca_cestas'),
    path('consulta_beneficiario/<int:pk>/', beneficiario_details, name='beneficiario_details'),
    path('buscar_cestas/<str:cpf>/', busca_cestas, name='busca_cestas_cpf'),

]
