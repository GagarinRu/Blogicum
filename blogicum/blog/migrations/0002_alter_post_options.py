# Generated by Django 3.2.16 on 2024-05-23 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'default_related_name': 'posts', 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
