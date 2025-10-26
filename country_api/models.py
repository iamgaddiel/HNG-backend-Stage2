from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capital = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    population = models.IntegerField()
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.FloatField(null=True, blank=True)
    estimated_gdp = models.FloatField(null=True, blank=True)
    flag_url = models.URLField(max_length=2048, null=True, blank=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Status(models.Model):
    last_refreshed_at = models.DateTimeField(null=True, blank=True)
    total_countries = models.IntegerField(default=0)