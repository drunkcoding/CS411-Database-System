# Generated by Django 2.2.5 on 2020-04-16 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gunviolence', '0002_auto_20200414_1348'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='incident_id',
            new_name='incident',
        ),
    ]
