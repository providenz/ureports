from django.db import models
from django.conf import settings
from reports.models import Project


class ProjectSharing(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="sharings"
    )
    shared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shared_projects",
    )
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_shares",
    )
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "shared_with")

        def __str__(self):
            return f"{self.shared_by} shared {self.project} with {self.shared_with} on {self.shared_at}"
