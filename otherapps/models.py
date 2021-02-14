from django.db import models

# Create your models here.

class Data(models.Model):
    desc = models.CharField(max_length=200)
    skills = models.CharField(max_length=200)

    def __str__(self):
        return self.desc