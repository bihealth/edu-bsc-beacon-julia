# Generated by Django 3.1.7 on 2021-03-29 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beacon', '0005_auto_20210329_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteSide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('key', models.CharField(max_length=255)),
                ('visibility_level', models.CharField(max_length=255)),
                ('access_limit', models.IntegerField()),
                ('consortium', models.ManyToManyField(help_text='Consortium to which this object belongs.', to='beacon.Consortium')),
            ],
        ),
    ]
