# app/api/models.py
from django.db import models

from app.api.assets.models import Asset
from app.api.incidents.models import Incident
from app.api.threat_intelligence.models import ThreatIntelligence
from app.api.vulnerabilities.models import Vulnerability


class AssetVulnerability(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='vulnerabilities')
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE, related_name='assets')
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
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='incident_assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='incident_assets')
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
