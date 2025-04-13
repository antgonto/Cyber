from django.db import models

from app.api.assets.models import Asset
from app.api.incidents.models import Incident
from app.api.vulnerabilities.models import Vulnerability


class ThreatIntelligence(models.Model):
    class ConfidenceLevelChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        VERY_HIGH = "very_high", "Very High"

    class IndicatorTypeChoices(models.TextChoices):
        IP = "ip", "IP Address"
        DOMAIN = "domain", "Domain"
        URL = "url", "URL"
        FILE_HASH = "file_hash", "File Hash"
        EMAIL = "email", "Email"
        OTHER = "other", "Other"

    threat_id = models.AutoField(primary_key=True)
    threat_actor_name = models.CharField(max_length=100)
    indicator_type = models.CharField(max_length=50, choices=IndicatorTypeChoices.choices)
    indicator_value = models.CharField(max_length=255)
    confidence_level = models.CharField(max_length=50, choices=ConfidenceLevelChoices.choices)
    description = models.TextField()
    related_cve = models.CharField(max_length=100, null=True, blank=True)
    date_identified = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Many-to-many relationships
    assets = models.ManyToManyField(Asset, through='ThreatAssetAssociation')
    vulnerabilities = models.ManyToManyField(Vulnerability, through='ThreatVulnerabilityAssociation')
    incidents = models.ManyToManyField(Incident, through='ThreatIncidentAssociation')

    class Meta:
        verbose_name = "Threat Intelligence"
        verbose_name_plural = "Threat Intelligence"

    def __str__(self):
        return f"{self.threat_actor_name} - {self.indicator_type}"



class ThreatAssetAssociation(models.Model):
    threat = models.ForeignKey(ThreatIntelligence, on_delete=models.CASCADE, related_name='asset_associations')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='threat_associations')

    class Meta:
        db_table = 'threat_asset_association'
        constraints = [models.UniqueConstraint(fields=['threat', 'asset'], name='unique_threat_asset')]
        verbose_name = "Threat Asset Association"
        verbose_name_plural = "Threat Asset Associations"
        indexes = [
            models.Index(fields=['threat_id'], name='idx_taa_threat_id'),
            models.Index(fields=['asset_id'], name='idx_taa_asset_id'),
        ]

    def __str__(self):
        return f"Threat {self.threat.threat_id} - Asset {self.asset.asset_name}"

class ThreatVulnerabilityAssociation(models.Model):
    threat = models.ForeignKey(ThreatIntelligence, on_delete=models.CASCADE,
                               related_name='vulnerability_associations')
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE, related_name='threat_associations')

    class Meta:
        db_table = 'threat_vulnerability_association'
        constraints = [models.UniqueConstraint(fields=['threat', 'vulnerability'], name='unique_threat_vulnerability')]
        verbose_name = "Threat Vulnerability Association"
        verbose_name_plural = "Threat Vulnerability Associations"
        indexes = [
            models.Index(fields=['threat_id'], name='idx_tva_threat_id'),
            models.Index(fields=['vulnerability_id'], name='idx_tva_vulnerability_id'),
        ]

    def __str__(self):
        return f"Threat {self.threat.threat_id} - Vulnerability {self.vulnerability.title}"


class ThreatIncidentAssociation(models.Model):
    threat = models.ForeignKey(ThreatIntelligence, on_delete=models.CASCADE, related_name='threat_incidents')
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='incident_threats')
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'threat_incident_association'
        constraints = [models.UniqueConstraint(fields=['threat', 'incident'], name='unique_threat_incident')]
        verbose_name = "Threat Incident Association"
        verbose_name_plural = "Threat Incident Associations"

        indexes = [
            models.Index(fields=['threat_id'], name='idx_tia_threat_id'),
            models.Index(fields=['incident_id'], name='idx_tia_incident_id'),
        ]

    def __str__(self):
        return f"Threat {self.threat.threat_id} - Incident {self.incident.incident_id}"