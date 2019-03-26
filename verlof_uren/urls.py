from django.contrib import admin
from django.conf.urls import url
from django.urls import include, path

# Verlof uren urls

urlpatterns = [
    # Admin urls (cool)
    path('admin/', admin.site.urls),
    url(r'^', include('django.contrib.auth.urls')),
]
