from django.db import models


class Alert(models.Model):
    class SeverityChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class StatusChoices(models.TextChoices):
        NEW = "new", "New"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    alert_id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=100)  # alert_type in SQL becomes type in model
    alert_time = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=50, choices=SeverityChoices.choices)
    status = models.CharField(max_length=50, choices=StatusChoices.choices, default=StatusChoices.NEW)
    incident = models.ForeignKey('Incident', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='alerts')

    def __str__(self):
        return f"{self.source} - {self.alert_type} ({self.severity})"

    class Meta:
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        indexes = [
            models.Index(fields=['incident_id'], name='idx_alert_incident_id'),
        ]