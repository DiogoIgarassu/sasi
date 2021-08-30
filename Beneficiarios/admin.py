from django.contrib import admin
from .models import Escolaridade, Localidade, UnidadeSuas, Bairro, Curso, Status
# Register your models here.

admin.site.register(Escolaridade)
admin.site.register(Localidade)
admin.site.register(UnidadeSuas)
admin.site.register(Bairro)
admin.site.register(Curso)
admin.site.register(Status)