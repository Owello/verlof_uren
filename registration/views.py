from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView
from django.http import HttpResponseRedirect

from .models import Entitlement, LeaveRegistration
from .forms import LeaveRegistrationForm, UserForm, EntitlementForm, AdminEntitlementForm

from django.contrib.auth.mixins import PermissionRequiredMixin


class Index(PermissionRequiredMixin, TemplateView):
    permission_required = 'registration.view_entitlement'
    template_name = 'registration/home.html'
    login_url = reverse_lazy('login')


class EntitlementList(PermissionRequiredMixin, ListView):
    permission_required = 'registration.view_entitlement'
    template_name = 'registration/entitlement_list.html'
    model = Entitlement
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(EntitlementList, self).get_context_data(**kwargs)
        entitlements = Entitlement.objects.filter(user=self.request.user).annotate_used_leave_hours()
        context['all_entitlements'] = entitlements
        return context


class EntitlementDetail(PermissionRequiredMixin, DetailView):
    permission_required = 'registration.view_entitlement'
    model = Entitlement
    login_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), user=self.request.user, year=self.kwargs['year'])

    def get_queryset(self):
        return super(EntitlementDetail, self).get_queryset().annotate_used_leave_hours()

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
    login_url = reverse_lazy('login')

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(LeaveRegistrationCreate, self).get_form_kwargs()
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
    login_url = reverse_lazy('login')

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(LeaveRegistrationUpdate, self).get_form_kwargs()
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


class UserList(PermissionRequiredMixin, ListView):
    permission_required = 'auth.view_user'
    template_name = 'registration/user_list.html'
    model = User
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return super(UserList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


class UserCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'auth.add_user'
    template_name = 'registration/user_create.html'
    model = User
    form_class = UserForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_password('welkom123!')
        self.object.save()
        form.save_m2m()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('user-list')


class UserUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'auth.change_user'
    template_name = 'registration/user_update.html'
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse_lazy('user-list')


class UserDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'auth.delete_user'
    model = User
    template_name = 'registration/user_confirm_delete.html'

    def get_queryset(self):
        return super(UserDelete, self).get_queryset()

    def get_success_url(self):
        return reverse_lazy('user-list')


class AdminEntitlementList(PermissionRequiredMixin, ListView):
    permission_required = ('auth.view_user', 'registration.change_entitlement')
    model = Entitlement
    template_name = 'registration/admin_entitlement_list.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(AdminEntitlementList, self).get_context_data(**kwargs)
        entitlements = Entitlement.objects.filter(user=self.kwargs['user_id']).annotate_used_leave_hours()
        context['all_entitlements'] = entitlements
        context['user_id'] = self.kwargs['user_id']
        return context


class AdminEntitlementDetail(PermissionRequiredMixin, DetailView):
    permission_required = ('auth.view_user', 'registration.change_entitlement')
    model = Entitlement
    template_name = 'registration/admin_entitlement_detail.html'
    login_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), user_id=self.kwargs['user_id'], year=self.kwargs['year'])

    def get_queryset(self):
        return super(AdminEntitlementDetail, self).get_queryset().annotate_used_leave_hours()

    def get_context_data(self, **kwargs):
        context = super(AdminEntitlementDetail, self).get_context_data(**kwargs)
        leave_registrations = LeaveRegistration.objects.filter(entitlement=self.object)
        context['all_leave_registrations'] = leave_registrations
        context['user_id'] = self.kwargs['user_id']
        return context


class AdminEntitlementCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('auth.view_user', 'registration.add_entitlement')
    template_name = 'registration/admin_entitlement_create.html'
    model = Entitlement
    form_class = EntitlementForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AdminEntitlementCreate, self).get_form_kwargs()
        all_entitlements = Entitlement.objects.filter(user=self.kwargs['user_id'])
        year = []
        for entitlement in all_entitlements:
            year.append(entitlement.year)
        kwargs['years'] = year
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user_id = self.kwargs['user_id']
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('admin-entitlement-list', kwargs={'user_id': self.object.user_id})


class AdminEntitlementUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('auth.view_user', 'registration.change_entitlement')
    template_name = 'registration/admin_entitlement_update.html'
    model = Entitlement
    form_class = AdminEntitlementForm

    def get_success_url(self):
        return reverse_lazy('admin-entitlement-list', kwargs={'user_id': self.object.user_id})


class AdminEntitlementDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('auth.view_user', 'registration.delete_entitlement')
    template_name = 'registration/admin_entitlement_delete.html'
    model = Entitlement

    def get_success_url(self):
        return reverse_lazy('admin-entitlement-list', kwargs={'user_id': self.object.user_id})


class AdminLeaveRegistrationCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('auth.view_user', 'registration.add_leaveregistration')
    template_name = 'registration/leaveregistration_create.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AdminLeaveRegistrationCreate, self).get_form_kwargs()
        all_entitlements = Entitlement.objects.filter(user=self.kwargs['user_id'])
        year = []
        for entitlement in all_entitlements:
            year.append(entitlement.year)
        kwargs['years'] = year
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.kwargs['user_id']
        self.object.entitlement = Entitlement.objects.get(user=self.object.user, year=self.object.from_date.year)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('admin-entitlement-detail',
                            kwargs={'user_id': self.object.entitlement.user_id, 'year': self.object.from_date.year})


class AdminLeaveRegistrationUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('auth.view_user', 'registration.change_leaveregistration')
    template_name = 'registration/admin_leaveregistration_update.html'
    model = LeaveRegistration
    form_class = LeaveRegistrationForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(AdminLeaveRegistrationUpdate, self).get_form_kwargs()
        all_entitlements = Entitlement.objects.filter(user_id=self.object.entitlement.user_id)
        year = []
        for entitlement in all_entitlements:
            year.append(entitlement.year)
        kwargs['years'] = year
        return kwargs

    def get_success_url(self):
        return reverse_lazy('admin-entitlement-detail',
                            kwargs={'user_id': self.object.entitlement.user_id, 'year': self.object.from_date.year})


class AdminLeaveRegistrationDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('auth.view_user', 'registration.delete_leaveregistration')
    template_name = 'registration/admin_leaveregistration_confirm_delete.html'
    model = LeaveRegistration

    def get_success_url(self):
        return reverse_lazy('admin-entitlement-detail',
                            kwargs={'user_id': self.object.entitlement.user_id, 'year': self.object.from_date.year})


class AdminUsersEntitlementList(PermissionRequiredMixin, ListView):
    permission_required = ('auth.view_user', 'registration.view_entitlement')
    template_name = 'registration/admin_users_entitlement_list.html'
    model = Entitlement
    login_url = reverse_lazy('login')

    def get_queryset(self):
        return super(AdminUsersEntitlementList, self).get_queryset() \
            .select_related('user') \
            .filter(year=self.kwargs['year']) \
            .annotate_used_leave_hours() \
            .order_by("-used_leave_hours")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AdminUsersEntitlementList, self).get_context_data()
        years = Entitlement.objects.values_list('year', flat=True).distinct()
        ordered_years = sorted(years)
        context['years'] = ordered_years
        leave_hours = Entitlement.objects.values_list('leave_hours', flat=True)
        total_leave_hours = sum(leave_hours)
        context['total_leave_hours'] = total_leave_hours
        amount_of_hours = LeaveRegistration.objects.values_list('amount_of_hours', flat=True)
        total_amount_of_hours = sum(amount_of_hours)
        context['total_amount_of_hours'] = total_amount_of_hours
        not_used_leave_hours = total_leave_hours - total_amount_of_hours
        context['not_used_leave_hours'] = not_used_leave_hours
        return context
