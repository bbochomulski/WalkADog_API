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


class Walk(models.Model):
    walk_id = models.AutoField(primary_key=True)
    dog_name = models.CharField(max_length=100)
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    trainer = models.CharField(max_length=100)
