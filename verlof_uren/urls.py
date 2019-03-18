from django.contrib import admin
from django.urls import path

urlpatterns = [
    # Admin urls
    path('admin/', admin.site.urls),
]
