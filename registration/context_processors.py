from registration.models import Entitlement
from datetime import datetime


def default_entitlement(request):
    if not request.user.is_authenticated:
        entitlement = None
    else:
        current_year = datetime.today().year
        try:
            entitlement = Entitlement.objects.get(user=request.user, year=current_year)
        except Entitlement.DoesNotExist:
            try:
                entitlement = Entitlement.objects.order_by('year').filter(user=request.user).last()
            except IndexError:
                entitlement = None
    return {
        'default_entitlement': entitlement
    }
