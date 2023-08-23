from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView

from cinema_app.models import *
from cinema_app.utils import DataContextMixin


# Create your views here.
class HomeView(DataContextMixin, ListView):
    model = Movie
    template_name = 'cinema_app/index.html'
    context_object_name = "movies"

    def get_queryset(self):
        movies = Movie.objects.filter(date_start__lte=datetime.now(), date_end__gte=datetime.now())
        query_name = self.request.GET.get('search_name')
        query_date = self.request.GET.get('search_date')
        if query_name:
            movies = movies.filter(movie_name__icontains=query_name)
        if query_date:
            query_date = datetime.strptime(query_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            movies = movies.filter(date_start__lte=query_date, date_end__gte=query_date)
        return movies

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        user_context = self.get_user_context(title="Главная", menu_tab_selected=1)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class MovieView(DataContextMixin, DetailView):
    model = Movie
    context_object_name = 'movie'
    template_name = "cinema_app/movie_details.html"
    slug_url_kwarg = 'movie_slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MovieView, self).get_context_data(**kwargs)
        current_movie = context.get('movie')

        sessions = Session.objects.filter(movie=current_movie).order_by('schedule__time')
        queryset = []
        search_filter = self.request.GET.get('search_date')
        search_filter = datetime.strptime(search_filter, '%d-%m-%Y') if search_filter else datetime.now()

        if search_filter.date() == datetime.now().date():
            for session in sessions:
                if session.date_session == search_filter.date() and session.schedule.time >= datetime.now().time():
                    queryset.append(session)
        elif search_filter.date() > datetime.now().date():
            for session in sessions:
                if session.date_session == search_filter.date():
                    queryset.append(session)

        context['movie_sessions'] = queryset
        context['session_date'] = search_filter.date()
        user_context = self.get_user_context(title=f"{current_movie}", menu_tab_selected=0)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class SessionView(LoginRequiredMixin, DataContextMixin, DetailView):
    model = Session
    context_object_name = 'session'
    template_name = 'cinema_app/session.html'
    pk_url_kwarg = 'session_pk'
    login_url = '/admin/'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SessionView, self).get_context_data(**kwargs)
        current_session: Session = context.get('session')
        context['tickets'] = Ticket.objects.filter(session=current_session).order_by('ticket_seat')
        user_context = self.get_user_context(title=f"Сеанс {current_session.schedule.time.strftime('%H:%M')}",
                                             menu_tab_selected=0)
        context = dict(list(context.items()) + list(user_context.items()))
        return context


class ConfirmOrderView(DataContextMixin, View):
    def post(self, *args, **kwargs):
        request_tickets = [value for key, value in self.request.POST.items() if key != 'csrfmiddlewaretoken']
        total_price = 0
        session = None
        tickets = []
        for ticket in Ticket.objects.filter(id__in=request_tickets):
            total_price += ticket.ticket_seat.category.price
            session = ticket.session
            tickets.append(ticket)

        user_context = self.get_user_context(title=f"Подтверждение заказа",
                                             menu_tab_selected=0)
        context = {
            'session': session,
            'tickets': tickets,
            'total_price': total_price
        }
        context = dict(list(context.items()) + list(user_context.items()))
        return render(self.request, 'cinema_app/confirm_order.html', context)


class CreateOrderView(DataContextMixin, View):
    def post(self, *args, **kwargs):
        tickets = [value for key, value in self.request.POST.items() if key != 'csrfmiddlewaretoken']
        for ticket in Ticket.objects.filter(id__in=tickets):
            if ticket.session.date_session == datetime.now().date() \
                    and ticket.session.schedule.time <= datetime.now().time():
                raise Http404("Сеанс не найден")
            ticket.user = self.request.user
            ticket.save()

        user_context = self.get_user_context(title=f"Заказ подтвержден",
                                             menu_tab_selected=0)
        return render(self.request, 'cinema_app/tickets_order_done.html', user_context)
