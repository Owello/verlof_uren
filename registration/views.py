from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView
from django.http import HttpResponseRedirect

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Entitlement, LeaveRegistration
from .forms import LeaveRegistrationForm


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


class LeaveRegistrationCreate(LoginRequiredMixin, CreateView):
    template_name = 'registration/leaveregistration_create.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm
    success_url = reverse_lazy('entitlement_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class LeaveRegistrationUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'registration/leaveregistration_update.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm
    success_url = reverse_lazy('entitlement_list')

    def get_queryset(self):
        return super(LeaveRegistrationUpdate, self).get_queryset().filter(user=self.request.user)
