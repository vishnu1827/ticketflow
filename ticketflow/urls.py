from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    # Django built-in auth for logout only; login overridden by our view
    path('auth/', include('django.contrib.auth.urls')),
]
