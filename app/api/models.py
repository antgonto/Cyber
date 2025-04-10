# app/api/models.py
from django.db import models


class AssetVulnerability(models.Model):
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, related_name='vulnerabilities')
    vulnerability = models.ForeignKey('Vulnerability', on_delete=models.CASCADE, related_name='assets')
    date_discovered = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50)

    class Meta:
        db_table = 'asset_vulnerabilities'
        constraints = [models.UniqueConstraint(fields=['asset', 'vulnerability'], name='unique_asset_vulnerability')]
        verbose_name = "Asset Vulnerability"
        verbose_name_plural = "Asset Vulnerabilities"
        indexes = [
            models.Index(fields=['asset_id'], name='idx_av_asset_id'),
            models.Index(fields=['vulnerability_id'], name='idx_asset_vulnerability_id'),
        ]

    def __str__(self):
        return f"{self.asset.asset_name} - {self.vulnerability.title}"


class IncidentAsset(models.Model):
    incident = models.ForeignKey('Incident', on_delete=models.CASCADE, related_name='incident_assets')
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, related_name='incident_assets')
    impact_level = models.CharField(max_length=100)

    class Meta:
        db_table = 'incident_assets'
        constraints = [models.UniqueConstraint(fields=['incident', 'asset'], name='unique_incident_asset')]
        verbose_name = "Incident Asset"
        verbose_name_plural = "Incident Assets"
        indexes = [
            models.Index(fields=['incident_id'], name='idx_incident_id'),
            models.Index(fields=['asset_id'], name='idx_asset_id_ia'),
        ]

    def __str__(self):
        return f"Incident {self.incident.incident_id} - Asset {self.asset.asset_name}"


class ThreatIncidentAssociation(models.Model):
    threat = models.ForeignKey('ThreatIntelligence', on_delete=models.CASCADE, related_name='threat_incidents')
    incident = models.ForeignKey('Incident', on_delete=models.CASCADE, related_name='incident_threats')
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

class ThreatAssetAssociation(models.Model):
    threat = models.ForeignKey('ThreatIntelligence', on_delete=models.CASCADE, related_name='asset_associations')
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, related_name='threat_associations')

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
    threat = models.ForeignKey('ThreatIntelligence', on_delete=models.CASCADE,
                               related_name='vulnerability_associations')
    vulnerability = models.ForeignKey('Vulnerability', on_delete=models.CASCADE, related_name='threat_associations')

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





