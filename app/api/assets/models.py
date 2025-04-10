from django.db import models


class Asset(models.Model):
    asset_id = models.AutoField(primary_key=True)
    asset_name = models.CharField(max_length=150, unique=True)
    asset_type = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    owner = models.CharField(max_length=100)
    criticality_level = models.CharField(max_length=50)

    def __str__(self):
        return self.asset_name

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"