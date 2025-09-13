
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path,include
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [

    path('admin/', admin.site.urls),
    path("api/", include("namjestaj.urls")),
    path('api/api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('', lambda request: redirect('/api/')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

