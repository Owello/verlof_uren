from django.conf.urls import url
from . import views
from .views import EntitlementList

urlpatterns = [
    url(r'^entitlementlist/', EntitlementList.as_view(), name='entitlement_list'),
    url(r'^$', views.Index.as_view(), name='index')
]
