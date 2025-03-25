from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db import IntegrityError
from .models import Client, ServiceOrganization, Manager
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Client)
def add_client_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user:
                group, created = Group.objects.get_or_create(name='Клиент')
                instance.user.groups.add(group)
                if created:
                    logger.info(f"Group 'Клиент' was created.")
                logger.info(f"User {instance.user.username} added to group 'Клиент'.")
            else:
                logger.warning(f"Client instance (ID: {instance.id}) has no associated user.")
        except IntegrityError as e:
            logger.error(f"Error adding user to group 'Клиент': {e}")

@receiver(post_save, sender=ServiceOrganization)
def add_service_org_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user:
                group, created = Group.objects.get_or_create(name='Сервисная организация')
                instance.user.groups.add(group)
                if created:
                    logger.info(f"Group 'Сервисная организация' was created.")
                logger.info(f"User {instance.user.username} added to group 'Сервисная организация'.")
            else:
                logger.warning(f"ServiceOrganization instance (ID: {instance.id}) has no associated user.")
        except IntegrityError as e:
            logger.error(f"Error adding user to group 'Сервисная организация': {e}")

@receiver(post_save, sender=Manager)
def add_manager_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user:
                group, created = Group.objects.get_or_create(name='Менеджер')
                instance.user.groups.add(group)
                if created:
                    logger.info(f"Group 'Менеджер' was created.")
                logger.info(f"User {instance.user.username} added to group 'Менеджер'.")
            else:
                logger.warning(f"Manager instance (ID: {instance.id}) has no associated user.")
        except IntegrityError as e:
            logger.error(f"Error adding user to group 'Менеджер': {e}")