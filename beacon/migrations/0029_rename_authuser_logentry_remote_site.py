# Generated by Django 3.2.2 on 2021-05-31 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("beacon", "0028_auto_20210531_1225"),
    ]

    operations = [
        migrations.RenameField(
            model_name="logentry",
            old_name="authuser",
            new_name="remote_site",
        ),
    ]
