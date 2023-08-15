from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, DetailView

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
        return redirect(reverse('home'))
