# Generated by Django 3.0.4 on 2020-03-26 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gunviolence', '0003_auto_20200322_2213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gunviolenceraw',
            name='incident_url_fields_missing',
            field=models.CharField(max_length=8, null=True),
        ),
    ]
