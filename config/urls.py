from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import login_view

urlpatterns = [
    path('', login_view, name='home'),

    path('admin/', admin.site.urls),

    path('', include('accounts.urls')),
    path('', include('dashboard.urls')),

    path('admin-panel/', include('adminpanel.urls')),

    # Agar courses kerak bo‘lsa pastda tursin
    path('courses/', include('courses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)