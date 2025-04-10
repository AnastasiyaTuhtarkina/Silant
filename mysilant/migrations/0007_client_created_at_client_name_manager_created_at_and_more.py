# Generated by Django 5.1.6 on 2025-03-24 19:11

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysilant', '0006_alter_technicalmaintenance_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='client',
            name='name',
            field=models.CharField(default='Default Name', max_length=255, verbose_name='Название компании'),
        ),
        migrations.AddField(
            model_name='manager',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='manager',
            name='name',
            field=models.CharField(default='Default Name', max_length=255, verbose_name='Имя менеджера'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='serviceorganization',
            name='name',
            field=models.CharField(default='Default Name', max_length=255, verbose_name='Название компании'),
        ),
    ]
