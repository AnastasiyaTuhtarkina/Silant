from django.apps import AppConfig

class MysilantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mysilant'

    def ready(self):
        import mysilant.signals  # Гарантируем, что сигналы импортируются здесь

        # Создание групп, только если они еще не существуют
        from django.contrib.auth.models import Group
        Group.objects.get_or_create(name='Клиент')
        Group.objects.get_or_create(name='Сервисная организация')
        Group.objects.get_or_create(name='Менеджер')