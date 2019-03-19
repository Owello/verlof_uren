from django.db import models


class Entitlement(models.Model):
    user = models.CharField(max_length=50)
    year = models.IntegerField()
    leave_hours = models.IntegerField()

    def __str__(self):
        return str(self.id)


class LeaveRegistration(models.Model):
    user = models.CharField(max_length=50)
    from_date = models.DateField()
    end_date = models.DateField()
    amount_of_hours = models.IntegerField()

    def __str__(self):
        return str(self.id)
