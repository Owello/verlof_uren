from django.urls import path
from . import views
from .views import EntitlementDetail, LeaveRegistrationCreate, LeaveRegistrationUpdate, LeaveRegistrationDelete, \
    EntitlementList, AdminUserList

urlpatterns = [
    path('entitlement/<int:year>', EntitlementDetail.as_view(), name='entitlement-detail'),
    path('leave_registration/create', LeaveRegistrationCreate.as_view(), name='leave_registration_create'),
    path('leave_registration/<int:pk>/update', LeaveRegistrationUpdate.as_view(),
         name='leave_registration_update'),
    path('leave_registration/<int:pk>/delete', LeaveRegistrationDelete.as_view(),
         name='leave_registration_delete'),
    path('entitlement_list', EntitlementList.as_view(), name='entitlement-list'),
    path('useradmin', AdminUserList.as_view(), name='adminuser-list'),
    path('', views.Index.as_view(), name='index')
]
