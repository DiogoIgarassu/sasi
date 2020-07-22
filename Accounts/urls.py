from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

app_name = 'Accounts'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('entrar/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('sair/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    path('cadastre-se/', register, name='register'),
    path('nova-senha/', password_reset, name='password_reset'),
    path('confirmar-nova-senha/?P<key>/', password_reset_confirm, name='password_reset_confirm'),
    path('editar/', edit, name='edit'),
    path('editar_senha/', edit_password, name='edit_password'),
]