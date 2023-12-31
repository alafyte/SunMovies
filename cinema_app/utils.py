main_menu = [
    {"id": 1, "title": "Главная", "url_name": "home"},
    {"id": 2, "title": "О кинотеатре", "url_name": "about"},
    {"id": 3, "title": "Цены", "url_name": "prices"},
    {"id": 4, "title": "Контакты", "url_name": "contacts"},
    {"id": 5, "title": "Информация", "url_name": "home"},
    {"id": 6, "title": "Регистрация", "url_name": "register"},
    {"id": 7, "title": "Войти", "url_name": "login"},
]


class DataContextMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['menu'] = main_menu
        if 'menu_tab_selected' not in context:
            context['menu_tab_selected'] = 1
        return context
