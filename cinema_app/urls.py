from django.conf.urls.static import static
from django.urls import path

from cinema_project import settings
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('search', SearchView.as_view(), name="search"),
    path('coming-soon', ComingSoonView.as_view(), name="coming-soon"),
    path('movie/<slug:movie_slug>/', MovieView.as_view(), name="movie"),
    path('movie/session/<int:session_pk>/', SessionView.as_view(), name="session"),
    path('about/', AboutView.as_view(), name="about"),
    path('prices/', PricesView.as_view(), name="prices"),
    path('contacts/', ContactsView.as_view(), name="contacts"),
    path('order/', CreateOrderView.as_view(), name="order"),
    path('confirm-order/', ConfirmOrderView.as_view(), name="confirm-order"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
