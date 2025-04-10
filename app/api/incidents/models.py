from django.db import models

from app.api.users.models import User


class Incident(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class SeverityChoices(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    incident_id = models.AutoField(primary_key=True)
    incident_type = models.CharField(max_length=100, verbose_name="Incident Type")
    description = models.TextField(verbose_name="Description")
    severity = models.CharField(max_length=50, choices=SeverityChoices.choices, verbose_name="Severity")
    status = models.CharField(
        max_length=50, choices=StatusChoices.choices, default=StatusChoices.OPEN, verbose_name="Status"
    )
    reported_date = models.DateTimeField(auto_now_add=True, verbose_name="Reported Date")
    resolved_date = models.DateTimeField(null=True, blank=True, verbose_name="Resolved Date")
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_incidents", verbose_name="Assigned To"
    )

    def __str__(self):
        return f"{self.incident_type} ({self.status})"

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"