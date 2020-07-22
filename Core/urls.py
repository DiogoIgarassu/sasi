from Core.views import *
from django.urls import path, include

app_name = 'core'
urlpatterns = [
    path('', home, name='home'),
    path('contato/', contact, name='contact'),
]
