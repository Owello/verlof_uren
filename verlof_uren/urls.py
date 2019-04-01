from django.contrib import admin
from django.urls import path
from django.urls import include

# Verlof uren urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', include('registration.urls')),
]
