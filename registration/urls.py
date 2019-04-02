from django.urls import path
from . import views
from .views import EntitlementDetail, LeaveRegistrationCreate, LeaveRegistrationUpdate, LeaveRegistrationDelete

urlpatterns = [
    path('entitlement/<int:year>', EntitlementDetail.as_view(), name='entitlement-detail'),
    path('leave_registration/create', LeaveRegistrationCreate.as_view(), name='leave_registration_create'),
    path('leave_registration/<int:pk>/update', LeaveRegistrationUpdate.as_view(),
         name='leave_registration_update'),
    path('leave_registration/<int:pk>/delete', LeaveRegistrationDelete.as_view(),
         name='leave_registration_delete'),
    path('', views.Index.as_view(), name='index')
]
