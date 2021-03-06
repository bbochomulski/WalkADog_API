# Generated by Django 4.0.4 on 2022-05-29 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0006_alter_dog_photo_alter_extendeduser_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dog',
            name='photo',
            field=models.ImageField(upload_to='dog_photos'),
        ),
        migrations.AlterField(
            model_name='extendeduser',
            name='photo',
            field=models.ImageField(upload_to='profile_photos'),
        ),
    ]
