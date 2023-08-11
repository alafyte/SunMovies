from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from cinema_app.models import *


# Create your views here.
class HomeView(ListView):
    model = Movie
    template_name = 'cinema_app/index.html'
    context_object_name = "movies"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context


class MovieView(DetailView):
    model = Movie
    context_object_name = 'movie'
    template_name = "cinema_app/movie_details.html"
    slug_url_kwarg = 'movie_slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MovieView, self).get_context_data(**kwargs)
        context['movie_sessions'] = Session.objects.filter(movie=context.get('movie'))
        return context


class SessionView(LoginRequiredMixin, DetailView):
    model = Session
    context_object_name = 'session'
    template_name = 'cinema_app/session.html'
    pk_url_kwarg = 'session_pk'
    login_url = '/admin/'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SessionView, self).get_context_data(**kwargs)
        current_session: Session = context.get('session')
        context['tickets'] = Ticket.objects.filter(session=current_session).order_by('ticket_seat')
        return context


class CreateOrderView(View):
    def post(self, request, *args, **kwargs):
        tickets = [value for key, value in self.request.POST.items() if key != 'csrfmiddlewaretoken']
        for ticket in Ticket.objects.filter(id__in=tickets):
            ticket.ordered = True
            ticket.user = request.user
            ticket.save()
        return HttpResponseRedirect(reverse('home'))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'cinema_app/login.html'

    def get_success_url(self):
        return reverse_lazy('home')


class RegisterUserView(CreateView):
    form_class = UserCreationForm
    template_name = 'cinema_app/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.success_url)
