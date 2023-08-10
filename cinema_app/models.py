from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.
class Movie(models.Model):
    movie_name = models.TextField(verbose_name="Название фильма")
    slug = models.SlugField(unique=True, db_index=True, verbose_name="URL")
    image = models.ImageField(upload_to="movie_images/%Y/%m", verbose_name="Постер")
    date_start = models.DateField(verbose_name="Дата начала проката")
    date_end = models.DateField(verbose_name="Дата окончания проката")
    age_rating = models.TextField(verbose_name="Возрастной рейтинг")
    duration = models.PositiveIntegerField(verbose_name="Длительность")
    genre = models.ForeignKey('Genre', related_name="genre", verbose_name="Жанр", on_delete=models.PROTECT)
    description = models.TextField(verbose_name="Описание")
    trailer = models.FileField(upload_to="movie_videos/%Y/%m", verbose_name="Трейлер")

    def __str__(self):
        return self.movie_name

    def get_absolute_url(self):
        return reverse('movie', kwargs={'movie_slug': self.slug})

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        ordering = ("date_start", "movie_name")


class Genre(models.Model):
    genre_name = models.TextField(verbose_name="Название жанра")

    def __str__(self):
        return self.genre_name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("genre_name",)


class Session(models.Model):
    date_session = models.DateField(verbose_name="Дата сеанса")
    time_session = models.TimeField(verbose_name="Время сеанса")
    movie = models.ForeignKey(Movie, related_name="movie", verbose_name="Фильм", on_delete=models.PROTECT)

    def __str__(self):
        return self.date_session.__str__() + " " + self.time_session.__str__()

    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеансы"
        ordering = ("date_session", "time_session")


class Seat(models.Model):
    hall = models.ForeignKey("Hall", related_name="hall", on_delete=models.PROTECT)
    row = models.PositiveIntegerField(verbose_name="Ряд")
    seat = models.PositiveIntegerField(verbose_name="Место")
    category = models.ForeignKey("Category", related_name="category", on_delete=models.PROTECT)

    def __str__(self):
        return self.hall.__str__() + ", ряд: " + self.row.__str__() + ", место: " + self.seat.__str__()

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ("hall", "row", "seat")


class Hall(models.Model):
    hall_name = models.TextField(verbose_name="Название зала")

    def __str__(self):
        return self.hall_name

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"
        ordering = ("hall_name",)


class Category(models.Model):
    category_name = models.TextField(verbose_name="Категория мест")
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = "Категория места"
        verbose_name_plural = "Категории мест"
        ordering = ("category_name",)


class Ticket(models.Model):
    order = models.ForeignKey("Order", related_name="order", verbose_name="Заказ", on_delete=models.PROTECT, null=True,
                              default=None)
    session = models.ForeignKey("Session", related_name="session", verbose_name="Сеанс", on_delete=models.PROTECT)
    ticket_seat = models.ForeignKey("Seat", related_name="ticket_seat", verbose_name="Место", on_delete=models.PROTECT)
    sold = models.BooleanField(default=False)


class Order(models.Model):
    date_of_order = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="user", verbose_name="Пользователь", on_delete=models.PROTECT)
