from django.contrib import admin
from django.conf.urls import url
from django.urls import include

# Verlof uren urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^', include('registration.urls')),
]
