from django.db import models

# Create your models here.


class Walk(models.Model):
    walk_id = models.AutoField(primary_key=True)
    dog_name = models.CharField(max_length=100)
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    trainer = models.CharField(max_length=100)
