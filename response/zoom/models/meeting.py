import logging
from datetime import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.db import models
from django.urls import reverse

from response.core.models.incident import Incident
from response.zoom.zoom import Zoom, ZoomClient

logger = logging.getLogger(__name__)


class MeetingManager(models.Manager):
    def create_meeting(self, incident):
        """
        Creates a zoom meeting, and saves a reference to it in the DB
        """
 
        z = Zoom().create(incident.summary, incident.summary)
        meeting = self.create(incident=incident, weblink=z["weblink"], challenge=z["challenge"])

        return meeting


class Meeting(models.Model):

    objects = MeetingManager()
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE)
    weblink = models.CharField(max_length=255, null=False)
    challenge = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.weblink
