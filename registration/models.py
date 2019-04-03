from django.contrib.auth.models import User
from django.db import models


class Entitlement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    leave_hours = models.IntegerField()

    def __str__(self):
        return '<Entitlement user={user} year={year}>'.format(user=self.user, year=self.year)

    class Meta:
        unique_together = ('user', 'year',)


class LeaveRegistration(models.Model):
    entitlement = models.ForeignKey(Entitlement, on_delete=models.CASCADE)
    from_date = models.DateField()
    end_date = models.DateField()
    amount_of_hours = models.IntegerField()

    def __str__(self):
        return str(self.id)
