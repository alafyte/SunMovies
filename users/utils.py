settings_tabs = [
    {"id": 1, "title": "На главную", "url_name": "home", "icon": "images/home.svg"},
    {"id": 2, "title": "Настройки", "url_name": "settings", "icon": "images/settings.svg"},
    {"id": 3, "title": "Сменить пароль", "url_name": "password_change", "icon": "images/change_pass.svg"},
    {"id": 4, "title": "Мои билеты", "url_name": "my_orders", "icon": "images/my_orders.svg"},
    {"id": 5, "title": "Выйти из аккаунта", "url_name": "logout", "icon": "images/logout.svg"},
]

tickets_tabs = [
    {'id': 1, "title": "Действующие", "url_name": "my_orders"},
    {'id': 2, "title": "Архив", "url_name": "archive_orders"}
]

movies_tabs = [
    {'id': 1, "title": "Сейчас в кино", "url_name": "home"},
    {'id': 2, "title": "Скоро в прокате", "url_name": "coming-soon"}
]


class SettingsContextMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['tabs'] = settings_tabs
        if 'tab_selected' not in context:
            context['tab_selected'] = 2
        return context


class MessageContextMixin:
    def get_session_context(self, request, message_types, **kwargs):
        context = kwargs
        for message_type in message_types:
            message = request.session.get(message_type)
            if message:
                context[message_type] = message
                del request.session[message_type]
        return context
