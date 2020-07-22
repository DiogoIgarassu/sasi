from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Core.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Core.urls', namespace='core')),
    path('conta/', include('Accounts.urls', namespace='accounts')),
    path('usuarios/', include('Usuarios.urls', namespace='usuarios')),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
