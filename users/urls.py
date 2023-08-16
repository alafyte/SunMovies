from django.conf.urls.static import static
from django.urls import path

from .forms import *
from .views import *
from django.contrib.auth.views import *

urlpatterns = [
    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path('register/', RegisterUserView.as_view(), name="register"),
    path('activate/<uidb64>/<token>', activation_view, name='activate'),
    path('accounts/password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/',
         PasswordResetView.as_view(template_name='users/password_reset_form.html', form_class=PasswordResetEmailForm),
         name='password_reset'),
    path('accounts/password_reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          form_class=SetNewPasswordForm),
         name='password_reset_confirm'),
    path('accounts/reset/done/', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
