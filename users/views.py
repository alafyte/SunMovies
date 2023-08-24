from datetime import datetime

import environ
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.contrib.auth import logout, login, get_user_model
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView, UpdateView, ListView

from cinema_app.models import Ticket
from cinema_app.utils import DataContextMixin
from .forms import LoginUserForm, RegisterUserForm, ProfileChangeForm, UserPasswordChangeForm, PasswordResetEmailForm, \
    SetNewPasswordForm
from .tokens import account_activation_token
from .utils import SettingsContextMixin, tickets_tabs, MessageContextMixin

# Create your views here.
User = get_user_model()
env = environ.Env()
env.read_env()


def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


class UserLoginView(DataContextMixin, MessageContextMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Вход", menu_tab_selected=6)
        session_context = self.get_session_context(self.request, message_types=['info_message', 'error_message'])
        context = dict(list(context.items()) + list(user_context.items()) + list(session_context.items()))
        return context


def activation_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None:
        if user.is_active:
            request.session['error_message'] = "Вы уже зарегистрированы, войдите в аккаунт"
            return redirect('login')
        elif account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('home')
        else:
            activate_email(request, user, user.email)
            request.session['error_message'] = "Срок действия ссылки истек. Мы отправили повторное " \
                                               "письмо-подтверждение. " \
                                               "Проверьте пожалуйста почту"
            return redirect('login')
    else:
        request.session['error_message'] = "Произошла ошибка регистрации. Повторите попытку"
        return redirect('register')


def activate_email(request, user, to_email):
    mail_subject = "Активация аккаунта."
    from_email = env('EMAIL_FROM')
    html_message = render_to_string("users/template_activate_account.html", {
        'username': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    plain_message = strip_tags(html_message)
    try:
        return send_mail(mail_subject, plain_message, from_email, [to_email], html_message=html_message)
    except:
        return False


class SettingsPageView(LoginRequiredMixin, SettingsContextMixin, MessageContextMixin, UpdateView):
    form_class = ProfileChangeForm
    template_name = 'users/account_settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        self.request.session["info_message"] = 'Успешно! Данные вашего профиля были обновлены'
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Настройки", tab_selected=2)
        session_context = self.get_session_context(self.request, message_types=['info_message'])
        context = dict(list(context.items()) + list(user_context.items()) + list(session_context.items()))
        return context


class OrdersView(SettingsContextMixin, ListView):
    template_name = 'users/orders.html'
    context_object_name = 'orders'
    model = Ticket
    paginate_by = 3

    def get_queryset(self):
        tickets = Ticket.objects.filter(user=self.request.user).order_by('-date_of_order')
        queryset = []
        for ticket in tickets:
            if datetime.combine(ticket.session.date_session, ticket.session.schedule.time) >= datetime.now():
                queryset.append(ticket)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Действующие билеты", tickets_tabs=tickets_tabs,
                                             tab_selected=4, tickets_tab_selected=1)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class ArchiveOrdersView(SettingsContextMixin, ListView):
    template_name = 'users/orders.html'
    context_object_name = 'orders'
    model = Ticket
    paginate_by = 3

    def get_queryset(self):
        tickets = Ticket.objects.filter(user=self.request.user).order_by('-date_of_order')
        queryset = []
        for ticket in tickets:
            if datetime.combine(ticket.session.date_session, ticket.session.schedule.time) < datetime.now():
                queryset.append(ticket)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Архив билетов", tickets_tabs=tickets_tabs,
                                             tab_selected=4, tickets_tab_selected=2)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class RegisterUserView(DataContextMixin, MessageContextMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        if activate_email(self.request, user, form.cleaned_data['email']):
            self.request.session["info_message"] = "Пожалуйста, подтвердите ваш email по ссылке в письме"
            return redirect('login')
        else:
            User.objects.get(id=user.id).delete()
            self.request.session["error_message"] = "Произошла ошибка при отправке письма-подтверждения. Пройдите " \
                                                    "процедуру " \
                                                    "регистрации заново, проверьте подключение и убедитесь в " \
                                                    "правильности введенных данных"
            return redirect('register')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_context = self.get_session_context(self.request, message_types=['error_message'])
        user_context = self.get_user_context(title="Регистрация", menu_tab_selected=5)
        context = dict(list(context.items()) + list(user_context.items()) + list(session_context.items()))
        return context


class UserPasswordChangeView(SettingsContextMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    form_class = UserPasswordChangeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Смена пароля", tab_selected=3)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class UserPasswordChangeDoneView(SettingsContextMixin, PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Пароль успешно изменен", tab_selected=3)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class UserPasswordResetView(PasswordResetView, DataContextMixin):
    template_name = 'users/password_reset_form.html'
    form_class = PasswordResetEmailForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Сброс пароля", menu_tab_selected=6)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class UserPasswordResetDoneView(DataContextMixin, PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Сброс пароля", menu_tab_selected=6)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class UserPasswordResetConfirmView(DataContextMixin, PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    form_class = SetNewPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Новый пароль", menu_tab_selected=6)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class UserPasswordResetCompleteView(DataContextMixin, PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title="Сброс пароля завершен", menu_tab_selected=6)
        context = dict(list(context.items()) + list(user_context.items()))
        return context
