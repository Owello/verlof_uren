from django.urls import path
from . import views
from .views import EntitlementDetail, LeaveRegistrationCreate, LeaveRegistrationUpdate, LeaveRegistrationDelete, EntitlementList, UserList, UserCreate, UserUpdate, UserDelete, \
    AdminEntitlementList, AdminEntitlementDetail, AdminEntitlementCreate, AdminEntitlementUpdate, AdminEntitlementDelete, AdminLeaveRegistrationDelete, \
    AdminLeaveRegistrationCreate, AdminLeaveRegistrationUpdate

urlpatterns = [
    path('entitlement/<int:year>', EntitlementDetail.as_view(), name='entitlement-detail'),
    path('leave_registration/create', LeaveRegistrationCreate.as_view(), name='leave-registration-create'),
    path('leave_registration/<int:pk>/update', LeaveRegistrationUpdate.as_view(),
         name='leave-registration-update'),
    path('leave_registration/<int:pk>/delete', LeaveRegistrationDelete.as_view(),
         name='leave-registration-delete'),
    path('entitlement_list', EntitlementList.as_view(), name='entitlement-list'),
    path('useradmin', UserList.as_view(), name='user-list'),
    path('useradmin/createuser', UserCreate.as_view(), name='user-create'),
    path('useradmin/<int:pk>/update', UserUpdate.as_view(), name='user-update'),
    path('useradmin/<int:pk>/delete', UserDelete.as_view(), name='user-delete'),
    path('useradmin/entitlement/<int:user_id>', AdminEntitlementList.as_view(),
         name='admin-entitlement-list'),
    path('useradmin/entitlement/<int:user_id>/<int:year>', AdminEntitlementDetail.as_view(),
         name='admin-entitlement-detail'),
    path('useradmin/entitlement/<int:user_id>/create', AdminEntitlementCreate.as_view(),
         name='admin-entitlement-create'),
    path('useradmin/entitlement/<int:pk>/update', AdminEntitlementUpdate.as_view(),
         name='admin-entitlement-update'),
    path('useradmin/entitlement/<int:pk>/delete', AdminEntitlementDelete.as_view(),
         name='admin-entitlement-delete'),
    path('useradmin/leave_registration/<int:user_id>/create', AdminLeaveRegistrationCreate.as_view(),
         name='admin-leaveregistration-create'),
    path('useradmin/leave_registration/<int:pk>/update', AdminLeaveRegistrationUpdate.as_view(),
         name='admin-leaveregistration-update'),
    path('useradmin/leave_registration/<int:pk>/delete', AdminLeaveRegistrationDelete.as_view(),
         name='admin-leaveregistration-delete'),
    path('', views.Index.as_view(), name='index')
]
