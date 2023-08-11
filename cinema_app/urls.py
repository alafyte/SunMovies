from django.conf.urls.static import static
from django.urls import path

from cinema_project import settings
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('movie/<slug:movie_slug>/', MovieView.as_view(), name="movie"),
    path('movie/session/<int:session_pk>/', SessionView.as_view(), name="session"),
    path('order/', CreateOrderView.as_view(), name="order"),
    path('login/', UserLoginView.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path('register/', RegisterUserView.as_view(), name="register")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
