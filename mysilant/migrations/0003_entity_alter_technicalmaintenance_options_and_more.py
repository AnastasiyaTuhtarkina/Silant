# Generated by Django 5.1.6 on 2025-03-11 12:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysilant', '0002_auto_20250311_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Сущность',
                'verbose_name_plural': 'Сущности',
            },
        ),
        migrations.AlterModelOptions(
            name='technicalmaintenance',
            options={'verbose_name': 'Тех.обслуживание', 'verbose_name_plural': 'Тех.обслуживание'},
        ),
        migrations.AlterUniqueTogether(
            name='reference',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='reference',
            name='entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='references', to='mysilant.entity'),
        ),
        migrations.AlterUniqueTogether(
            name='reference',
            unique_together={('entity', 'name')},
        ),
        migrations.RemoveField(
            model_name='reference',
            name='entity_name',
        ),
    ]
