from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class MysilantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mysilant'

    def ready(self):
        import mysilant.signals  # Гарантируем, что сигналы импортируются здесь

        # Создание групп, только если они еще не существуют
        from django.contrib.auth.models import Group
        from django.db import IntegrityError

        try:
            Group.objects.get_or_create(name='Клиент')
            Group.objects.get_or_create(name='Сервисная организация')
            Group.objects.get_or_create(name='Менеджер')
            logger.info("Группы успешно созданы или уже существуют.")
        except IntegrityError as e:
            logger.error(f"Ошибка при создании групп: {e}")