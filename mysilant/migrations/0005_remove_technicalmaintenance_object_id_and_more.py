# Generated by Django 5.1.6 on 2025-03-13 10:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysilant', '0004_alter_claim_downtime_duration_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='technicalmaintenance',
            name='object_id',
        ),
        migrations.AlterField(
            model_name='technicalmaintenance',
            name='content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mysilant.serviceorganization', verbose_name='Организация, проводившая ТО'),
        ),
    ]
