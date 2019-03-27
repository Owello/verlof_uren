from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Entitlement, LeaveRegistration


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'registration/home.html'
    login_url = reverse_lazy('login')


class EntitlementList(LoginRequiredMixin, TemplateView):
    template_name = 'registration/entitlementlist.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(EntitlementList, self).get_context_data(**kwargs)
        context['all_entitlements'] = Entitlement.objects.filter(user=self.request.user)
        context['all_leave_registrations'] = LeaveRegistration.objects.filter(user=self.request.user)
        # next two additions have to be calculated instead of 0
        context['used_leave_hours'] = 0
        context['remainder_leave_hours'] = 0
        return context
