# Generated by Django 3.1.7 on 2021-03-29 07:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("beacon", "0003_auto_20210325_0855"),
    ]

    operations = [
        migrations.CreateModel(
            name="LogEntry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip_address", models.CharField(max_length=15)),
                ("user_identifier", models.CharField(max_length=255)),
                ("date_time", models.DateTimeField()),
                ("request", models.CharField(max_length=255)),
                ("status_code", models.IntegerField()),
                ("response_size", models.IntegerField()),
                (
                    "frank",
                    models.ForeignKey(
                        help_text="Consortium to which the client belongs to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="beacon.consortium",
                    ),
                ),
            ],
        ),
    ]
