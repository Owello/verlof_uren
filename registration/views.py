from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Entitlement, LeaveRegistration
from .forms import LeaveRegistrationForm


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'registration/home.html'
    login_url = reverse_lazy('login')


class EntitlementDetail(LoginRequiredMixin, DetailView):
    model = Entitlement
    login_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return get_object_or_404(Entitlement, user=self.request.user, year=self.kwargs['year'])

    def get_context_data(self, **kwargs):
        context = super(EntitlementDetail, self).get_context_data(**kwargs)
        leave_registrations = LeaveRegistration.objects.filter(user=self.request.user, from_date__year=self.object.year)
        context['all_leave_registrations'] = leave_registrations

        hours_total = 0
        for leave_registration in leave_registrations:
            hours_total += leave_registration.amount_of_hours
        context['used_leave_hours'] = hours_total

        context['remainder_leave_hours'] = self.object.leave_hours - hours_total
        return context


class LeaveRegistrationCreate(LoginRequiredMixin, CreateView):
    template_name = 'registration/leaveregistration_create.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('entitlement-detail', kwargs={'year': self.object.from_date.year})


class LeaveRegistrationUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'registration/leaveregistration_update.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm

    def get_queryset(self):
        return super(LeaveRegistrationUpdate, self).get_queryset().filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('entitlement-detail', kwargs={'year': self.object.from_date.year})


class LeaveRegistrationDelete(LoginRequiredMixin, DeleteView):
    model = LeaveRegistration

    def get_queryset(self):
        return super(LeaveRegistrationDelete, self).get_queryset().filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('entitlement-detail', kwargs={'year': self.object.from_date.year})
