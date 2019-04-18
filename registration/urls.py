from django.urls import path
from . import views
from .views import EntitlementDetail, LeaveRegistrationCreate, LeaveRegistrationUpdate, LeaveRegistrationDelete, \
    EntitlementList, UserList, UserCreate, UserUpdate

urlpatterns = [
    path('entitlement/<int:year>', EntitlementDetail.as_view(), name='entitlement-detail'),
    path('leave_registration/create', LeaveRegistrationCreate.as_view(), name='leave_registration_create'),
    path('leave_registration/<int:pk>/update', LeaveRegistrationUpdate.as_view(),
         name='leave_registration_update'),
    path('leave_registration/<int:pk>/delete', LeaveRegistrationDelete.as_view(),
         name='leave_registration_delete'),
    path('entitlement_list', EntitlementList.as_view(), name='entitlement-list'),
    path('useradmin', UserList.as_view(), name='user-list'),
    path('useradmin/createuser', UserCreate.as_view(), name='user-create'),
    path('useradmin/updateuser/<int:pk>', UserUpdate.as_view(), name='user-update'),
    path('', views.Index.as_view(), name='index')
]
