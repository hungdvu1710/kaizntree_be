from django.db import models

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    SKU = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100)
    tags = models.ManyToManyField(Tag, blank=True)
    stock_status = models.CharField(max_length=100)
    available_stock = models.IntegerField()

    def __str__(self):
        return self.name
