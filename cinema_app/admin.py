from django.contrib import admin
from .models import *


# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    search_fields = ('movie_name', )
    prepopulated_fields = {"slug": ("movie_name", )}


class SessionAdmin(admin.ModelAdmin):
    readonly_fields = ('date_session', 'movie', 'schedule')


admin.site.register(Movie, MovieAdmin)
admin.site.register(Seat)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Hall)
admin.site.register(Session, SessionAdmin)
admin.site.register(Schedule)
admin.site.register(Ticket)
