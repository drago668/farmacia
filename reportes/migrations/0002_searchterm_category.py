# Generated by Django 5.2.1 on 2025-05-17 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchterm',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
