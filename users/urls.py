from django.conf.urls.static import static
from django.urls import path

from cinema_project import settings
from .views import *

urlpatterns = [
    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path('register/', RegisterUserView.as_view(), name="register"),
    path('activate/<uidb64>/<token>', activate, name='activate')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)