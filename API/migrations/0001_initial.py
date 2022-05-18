# Generated by Django 4.0.4 on 2022-05-12 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Walk',
            fields=[
                ('walk_id', models.AutoField(primary_key=True, serialize=False)),
                ('dog_name', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('start_hour', models.TimeField()),
                ('end_hour', models.TimeField()),
                ('trainer', models.CharField(max_length=100)),
            ],
        ),
    ]