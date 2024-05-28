from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from blog.views import RegistrationCreate


urlpatterns = [
    path('admin/', admin.site.urls, ),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        RegistrationCreate.as_view(),
        name='registration',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
