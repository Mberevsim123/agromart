from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('management/', include('management.urls')),
    path('favicon.ico', lambda request: HttpResponse(status=204)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
