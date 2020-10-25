from datetime import datetime

from django.db import models
from jsonfield import JSONField

from response.core.models.incident import Incident
from response.core.models.user_external import ExternalUser
from response.core.util import sanitize


class StatusUpdate(models.Model):

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(
        null=False, default=datetime.now, help_text="Time of when this update was added."
    )
    text = models.TextField(help_text="Freeform text to provide status")
    user = models.ForeignKey(
        ExternalUser, on_delete=models.CASCADE, blank=False, null=False
    )
    def save(self, *args, **kwargs):
        self.text = sanitize(self.text)
        super(StatusUpdate, self).save(*args, **kwargs)
