from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from .models import Client, ServiceOrganization, Manager
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Client)
def add_client_to_group(sender, instance, created, **kwargs):
    if created:
        # Убедитесь, что у клиента есть связанный пользователь
        if instance.user:
            group, created = Group.objects.get_or_create(name='Клиент')
            instance.user.groups.add(group)
            if created:
                logger.info(f"Group 'Клиент' was created.")
            logger.info(f"User {instance.user.username} added to group 'Клиент'.")
        else:
            logger.warning("Client instance has no associated user.")

@receiver(post_save, sender=ServiceOrganization)
def add_service_org_to_group(sender, instance, created, **kwargs):
    if created:
        if instance.user:
            group = Group.objects.get(name='Сервисная организация')
            instance.user.groups.add(group)
            logger.info(f"User {instance.user.username} added to group 'Сервисная организация'.")
        else:
            logger.warning("The group 'Сервисная организация' does not exist.") 


@receiver(post_save, sender=Manager)
def add_manager_to_group(sender, instance, created, **kwargs):
    if created:
        if instance.user:
            group = Group.objects.get(name='Менеджер')
            instance.user.groups.add(group)
            logger.info(f"User {instance.user.username} added to group 'Менеджер'.")
        else:
            logger.warning("The group 'Менеджер' does not exist.") 