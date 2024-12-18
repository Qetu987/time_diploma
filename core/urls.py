from django.contrib import admin
from django.urls import path, include
from core import settings
from django.conf.urls.static import static
from user.views import BasePage



urlpatterns = [
    path('', BasePage.as_view(), name='base_page'),
    path('project/', include('project.urls')),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
