from django.db import models


class ThreatIntelligence(models.Model):
    class ConfidenceLevelChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        VERY_HIGH = "very_high", "Very High"

    threat_id = models.AutoField(primary_key=True)
    threat_actor_name = models.CharField(max_length=100)
    indicator_type = models.CharField(max_length=50)
    indicator_value = models.CharField(max_length=255)
    confidence_level = models.CharField(max_length=50, choices=ConfidenceLevelChoices.choices)
    description = models.TextField()
    related_cve = models.CharField(max_length=100, null=True, blank=True)

    # Many-to-many relationships
    assets = models.ManyToManyField('Asset', through='ThreatAssetAssociation')
    vulnerabilities = models.ManyToManyField('Vulnerability', through='ThreatVulnerabilityAssociation')
    incidents = models.ManyToManyField('Incident', through='ThreatIncidentAssociation')

    class Meta:
        verbose_name = "Threat Intelligence"
        verbose_name_plural = "Threat Intelligence"

    def __str__(self):
        return f"{self.threat_actor_name} - {self.indicator_type}"