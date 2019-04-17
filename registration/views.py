from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView
from django.http import HttpResponseRedirect

from .models import Entitlement, LeaveRegistration
from .forms import LeaveRegistrationForm

from django.contrib.auth.mixins import PermissionRequiredMixin


class Index(PermissionRequiredMixin, TemplateView):
    permission_required = 'registration.view_entitlement'
    template_name = 'registration/home.html'
    login_url = reverse_lazy('login')


class EntitlementDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'registration.view_entitlement'
    model = Entitlement
    login_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), user=self.request.user, year=self.kwargs['year'])

    def get_queryset(self):
        return super(EntitlementDetail, self).get_queryset().annotate(
            used_leave_hours=Coalesce(Sum('leaveregistration__amount_of_hours'), 0))

    def get_context_data(self, **kwargs):
        context = super(EntitlementDetail, self).get_context_data(**kwargs)
        context['all_entitlements'] = Entitlement.objects.filter(user=self.request.user)
        leave_registrations = LeaveRegistration.objects.filter(entitlement=self.object)
        context['all_leave_registrations'] = leave_registrations
        return context


class LeaveRegistrationCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'registration.add_leaveregistration'
    template_name = 'registration/leaveregistration_create.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(LeaveRegistrationCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        all_entitlements = Entitlement.objects.filter(user=self.request.user)
        year = []
        for entitlement in all_entitlements:
            year.append(entitlement.year)
        kwargs['years'] = year
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.entitlement = Entitlement.objects.get(user=self.object.user, year=self.object.from_date.year)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('entitlement-detail', kwargs={'year': self.object.from_date.year})


class LeaveRegistrationUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'registration.change_leaveregistration'
    template_name = 'registration/leaveregistration_update.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(LeaveRegistrationUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        all_entitlements = Entitlement.objects.filter(user=self.request.user)
        year = []
        for entitlement in all_entitlements:
            year.append(entitlement.year)
        kwargs['years'] = year
        return kwargs

    def get_queryset(self):
        return super(LeaveRegistrationUpdate, self).get_queryset().filter(entitlement__user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('entitlement-detail', kwargs={'year': self.object.from_date.year})


class LeaveRegistrationDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'registration.delete_leaveregistration'
    model = LeaveRegistration

    def get_queryset(self):
        return super(LeaveRegistrationDelete, self).get_queryset().filter(entitlement__user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('entitlement-detail', kwargs={'year': self.object.from_date.year})


class EntitlementList(PermissionRequiredMixin, ListView):
    permission_required = 'registration.view_entitlement'
    template_name = 'registration/entitlement_list.html'
    model = Entitlement
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(EntitlementList, self).get_context_data(**kwargs)
        entitlements = Entitlement.objects.filter(user=self.request.user).annotate(
            used_leave_hours=Coalesce(Sum('leaveregistration__amount_of_hours'), 0))
        context['all_entitlements'] = entitlements
        return context


class AdminUserList(PermissionRequiredMixin, ListView):
    permission_required = 'auth.view_user'
    template_name = 'registration/admin_user_list.html'
    model = User
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return super(AdminUserList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(AdminUserList, self).get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


