from django.db import models

# Create your models here.

class Sites(models.Model):
    name = models.CharField(max_length=100)


    def __str__(self):
        return self.name


class AllData(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255,null=True, blank=True)
    old_price = models.CharField(max_length=255,null=True, blank=True)
    total_ratings = models.CharField(max_length=255,null=True, blank=True)
    avg_rating = models.CharField(max_length=255,null=True, blank=True)
    new_price = models.CharField(max_length=255,null=True, blank=True)
    discount_percentage = models.CharField(max_length=255,null=True, blank=True)
    link = models.CharField(max_length=1000,null=True, blank=True)
    image = models.CharField(max_length=2550,null=True, blank=True)
    discount = models.CharField(max_length=255,null=True, blank=True)
    category = models.CharField(max_length=255,null=True, blank=True)
    site = models.ForeignKey(Sites, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         orders if retrieved'''
        ordering = ('name',)

    def __str__(self):
        return self.name
