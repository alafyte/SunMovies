from django.contrib import admin
from .models import *


# Register your models here.
class MovieAdmin(admin.ModelAdmin):
    search_fields = ('movie_name', )
    prepopulated_fields = {"slug": ("movie_name", )}


admin.site.register(Movie, MovieAdmin)
admin.site.register(Seat)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Hall)
admin.site.register(Session)
admin.site.register(Schedule)
