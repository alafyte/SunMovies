from django.conf.urls.static import static
from django.urls import path

from .views import *
import cinema_project.settings as settings

urlpatterns = [
    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path('register/', RegisterUserView.as_view(), name="register"),
    path('activate/<uidb64>/<token>', activation_view, name='activate'),
    path('settings/', SettingsPageView.as_view(), name="settings"),
    path('my_orders', OrdersView.as_view(), name="my_orders"),
    path('password_change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', UserPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
