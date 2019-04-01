from django.urls import path
from . import views
from .views import EntitlementList, LeaveRegistrationCreate, LeaveRegistrationUpdate

urlpatterns = [
    path('entitlementlist/', EntitlementList.as_view(), name='entitlement_list'),
    path('leave_registration/create', LeaveRegistrationCreate.as_view(), name='leave_registration_create'),
    path('leave_registration/<int:pk>/update', LeaveRegistrationUpdate.as_view(),
         name='leave_registration_update'),
    path('', views.Index.as_view(), name='index')
]
