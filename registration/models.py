from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce


class EntitlementQueryset(models.QuerySet):
    def annotate_used_leave_hours(self):
        return self.annotate(used_leave_hours=Coalesce(Sum('leaveregistration__amount_of_hours'), 0))


class EntitlementManager(models.Manager.from_queryset(EntitlementQueryset)):
    pass


class Entitlement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    leave_hours = models.IntegerField()

    objects = EntitlementManager()

    class Meta:
        unique_together = ('user', 'year',)

    def __str__(self):
        return '<Entitlement user={user} year={year}>'.format(user=self.user, year=self.year)

    def get_remainder_hours(self):
        return self.leave_hours - self.get_used_hours()

    def get_used_hours(self):
        if not hasattr(self, 'used_leave_hours'):
            raise AttributeError(
                'used_leave_hours not available on Entitlement instance. Annotate the Entitlement query with annotate_used_leave_hours()')
        return self.used_leave_hours

    def get_color(self):
        amount = self.get_remainder_hours()
        if amount < 0:
            return 'red'
        elif amount >= 25:
            return 'green'
        return 'orange'


class LeaveRegistration(models.Model):
    entitlement = models.ForeignKey(Entitlement, on_delete=models.CASCADE)
    from_date = models.DateField()
    end_date = models.DateField()
    amount_of_hours = models.IntegerField()

    def __str__(self):
        return str(self.id)
