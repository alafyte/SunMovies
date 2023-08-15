from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth import logout, login, get_user_model
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView

from .forms import LoginUserForm, RegisterUserForm
from .tokens import account_activation_token


# Create your views here.
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
        context['user_registered'] = self.request.session.get('user_registered')
        context['user_email_confirmed'] = self.request.session.get('user_email_confirmed')
        return context


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        request.session["user_registered"] = False
        request.session["user_email_confirmed"] = True
        return redirect('login')

    return redirect('home')


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
    return email.send()


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        if activate_email(self.request, user, form.cleaned_data['email']):
            self.request.session['user_registered'] = True
        return redirect(self.success_url)
