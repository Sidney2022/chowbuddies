from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions 
from drf_yasg.views import get_schema_view 
from drf_yasg import openapi 
# from .import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve





urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('base.urls')),

    
]

if  settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

else:
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ]


handler404 = 'base.views.error_404'
handler500 = 'base.views.error_500'
