from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Contact(models.Model):
    hrefname=models.CharField(max_length=30)
    email = models.EmailField(max_length=40)

    def __str__(self):
        return self.hrefname
