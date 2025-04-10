from django.db import models


class Vulnerability(models.Model):
    vulnerability_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    severity = models.CharField(max_length=50)
    cve_reference = models.CharField(max_length=100)
    remediation_steps = models.TextField()
    discovery_date = models.DateTimeField(null=True, blank=True)
    patch_available = models.BooleanField(default=True)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Vulnerability"
        verbose_name_plural = "Vulnerabilities"