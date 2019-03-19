from django.contrib import admin
from .models import Entitlement, LeaveRegistration


class EntitlementAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'leave_hours')
    list_filter = ('user', 'year')


class LeaveRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_date', 'end_date', 'amount_of_hours')
    list_filter = ('user',)


admin.site.register(Entitlement, EntitlementAdmin)
admin.site.register(LeaveRegistration, LeaveRegistrationAdmin)
