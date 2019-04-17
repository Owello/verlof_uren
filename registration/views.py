from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Entitlement, LeaveRegistration
from .forms import LeaveRegistrationForm


from django.contrib.auth.mixins import PermissionRequiredMixin


class PermissionView(PermissionRequiredMixin, TemplateView):
    permission_required = 'registration.can_view'
    permission_required = 'registration.can_add'
    permission_required = 'registration.can_delete'


class Index(LoginRequiredMixin, TemplateView):
    template_name = 'registration/home.html'
    login_url = reverse_lazy('login')


class EntitlementDetail(LoginRequiredMixin, DetailView):
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


class LeaveRegistrationCreate(LoginRequiredMixin, CreateView):
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


class LeaveRegistrationUpdate(LoginRequiredMixin, UpdateView):
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


class LeaveRegistrationDelete(LoginRequiredMixin, DeleteView):
    model = LeaveRegistration

    def get_queryset(self):
        return super(LeaveRegistrationDelete, self).get_queryset().filter(entitlement__user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('entitlement-detail', kwargs={'year': self.object.from_date.year})


class EntitlementList(LoginRequiredMixin, ListView):
    template_name = 'registration/entitlement_list.html'
    model = Entitlement
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(EntitlementList, self).get_context_data(**kwargs)
        entitlements = Entitlement.objects.filter(user=self.request.user).annotate(
            used_leave_hours=Coalesce(Sum('leaveregistration__amount_of_hours'), 0))
        context['all_entitlements'] = entitlements
        return context


class AdminUserList(LoginRequiredMixin, ListView):
    template_name = 'registration/admin_user_list.html'
    model = User
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return super(AdminUserList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(AdminUserList, self).get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


