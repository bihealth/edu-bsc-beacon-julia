# Generated by Django 3.2.2 on 2021-05-12 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("beacon", "0024_alter_remotesite_consortia"),
    ]

    operations = [
        migrations.AlterField(
            model_name="variant",
            name="chromosome",
            field=models.IntegerField(
                choices=[
                    (1, "1"),
                    (2, "2"),
                    (3, "3"),
                    (4, "4"),
                    (5, "5"),
                    (6, "6"),
                    (7, "7"),
                    (8, "8"),
                    (9, "9"),
                    (10, "10"),
                    (11, "11"),
                    (12, "12"),
                    (13, "13"),
                    (14, "14"),
                    (15, "15"),
                    (16, "16"),
                    (17, "17"),
                    (18, "18"),
                    (19, "19"),
                    (20, "20"),
                    (21, "21"),
                    (22, "22"),
                    (23, "X"),
                    (24, "Y"),
                ]
            ),
        ),
    ]
