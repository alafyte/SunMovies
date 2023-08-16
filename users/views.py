from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth import logout, login, get_user_model
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView

from .forms import LoginUserForm, RegisterUserForm
from .tokens import account_activation_token

# Create your views here.
User = get_user_model()


def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


class UserLoginView(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = self.request.session.get('info_message')
        if message:
            context['info_message'] = message
            del self.request.session['info_message']
        message = self.request.session.get('error_message')
        if message:
            context['error_message'] = message
            del self.request.session['error_message']
        return context


def activation_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None:
        if account_activation_token.check_token(user, token):
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
    mail_subject = "Activate your user account."
    message = render_to_string("users/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    try:
        return email.send()
    except:
        return False


class RegisterUserView(CreateView):
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
                                                    "регистрации заново и убедитесь в правильности введенных данных"
            return redirect('register')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = self.request.session.get('error_message')
        if message:
            context['error_message'] = message
            del self.request.session['error_message']
        return context
