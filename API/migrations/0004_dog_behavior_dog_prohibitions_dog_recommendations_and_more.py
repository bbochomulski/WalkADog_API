# Generated by Django 4.0.4 on 2022-05-29 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0003_alter_walk_dog_alter_walk_trainer'),
    ]

    operations = [
        migrations.AddField(
            model_name='dog',
            name='behavior',
            field=models.TextField(default='No behavior'),
        ),
        migrations.AddField(
            model_name='dog',
            name='prohibitions',
            field=models.TextField(default='No prohibitions'),
        ),
        migrations.AddField(
            model_name='dog',
            name='recommendations',
            field=models.TextField(default='No recommendations'),
        ),
        migrations.AlterField(
            model_name='dog',
            name='description',
            field=models.TextField(default='No description'),
        ),
        migrations.AlterField(
            model_name='dog',
            name='photo',
            field=models.ImageField(upload_to='dog_photos'),
        ),
    ]