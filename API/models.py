from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

    for user in User.objects.all():
        Token.objects.get_or_create(user=user)


class ExtendedUser(User):
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    photo = models.ImageField(upload_to='profile_photos', blank=False, null=False)


class Client(ExtendedUser):
    client_id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Dog(models.Model):
    dog_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    breed = models.CharField(max_length=200)
    age = models.IntegerField()
    description = models.TextField(default='No description')
    behavior = models.TextField(default='No behavior')
    prohibitions = models.TextField(default='No prohibitions')
    recommendations = models.TextField(default='No recommendations')
    owner = models.ForeignKey(Client, on_delete=models.CASCADE, null=False)
    photo = models.ImageField(upload_to='dog_photos', null=True, blank=True)

    def __str__(self):
        return self.name


class Trainer(ExtendedUser):
    trainer_id = models.AutoField(primary_key=True)
    date_of_birth = models.DateField()
    experience = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Walk(models.Model):
    walk_id = models.AutoField(primary_key=True)
    dog = models.ForeignKey(Dog, on_delete=models.DO_NOTHING, null=False, default=1)
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    trainer = models.ForeignKey(Trainer, on_delete=models.DO_NOTHING, null=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.dog.name} - {str(self.trainer)} - {self.date.strftime('%d/%m/%Y')}"


class TrainerReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, null=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=False)
    date = models.DateField()
    rating = models.IntegerField()
    comment = models.TextField()
    walk_id = models.ForeignKey(Walk, on_delete=models.DO_NOTHING, default=None, null=True)


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateField()
    read = models.BooleanField()


class Coordinates(models.Model):
    coordinates_id = models.AutoField(primary_key=True)
    latitude_start = models.FloatField()
    longitude_start = models.FloatField()
    latitude_end = models.FloatField()
    longitude_end = models.FloatField()
    walk = models.ForeignKey(Walk, on_delete=models.CASCADE, null=False)


class TrainerAvailability(models.Model):
    availability_id = models.AutoField(primary_key=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, null=False)
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    active = models.BooleanField(default=True)


class Position(models.Model):
    position_id = models.AutoField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date = models.DateField()
    walk = models.ForeignKey(Walk, on_delete=models.CASCADE, null=False)
