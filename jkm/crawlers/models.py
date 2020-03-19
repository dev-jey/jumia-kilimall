from django.db import models

# Create your models here.

class Sites(models.Model):
    name = models.CharField(max_length=100)


class AllData(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    old_price = models.CharField(max_length=100)
    total_ratings = models.CharField(max_length=100)
    avg_rating = models.CharField(max_length=100)
    new_price = models.CharField(max_length=100)
    discount_percentage = models.CharField(max_length=100)
    link = models.CharField(max_length=1000)
    image = models.CharField(max_length=1000)
    discount = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    site = models.ForeignKey(Sites, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         orders if retrieved'''
        ordering = ('name',)

    def __str__(self):
        return self.name
