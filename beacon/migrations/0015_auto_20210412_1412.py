# Generated by Django 3.1.7 on 2021-04-12 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('beacon', '0014_auto_20210407_0716'),
    ]

    operations = [
        migrations.RenameField(
            model_name='metadatabeacondataset',
            old_name='beacon_id',
            new_name='beacon_metadata',
        ),
        migrations.RenameField(
            model_name='metadatabeaconorganization',
            old_name='beacon_id',
            new_name='beacon_metadata',
        ),
    ]