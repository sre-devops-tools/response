import logging
from datetime import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.db import models
from django.urls import reverse

from response.core.models.incident import Incident
from response.slack.client import SlackError

logger = logging.getLogger(__name__)


class MeetingManager(models.Manager):
    def create_meeting(self, incident):
        """
        Creates a zoom meeting, and saves a reference to it in the DB
        """
        time_string = datetime.now().strftime("%b-%-e-%H-%M-%S")

        try:
          
        except SlackError as e:
            logger.error(f"Failed to create comms channel {e}")
            raise

        # # If the channel already existed we will need to join it
        # # If we are already in the channel as we created it, then this is a No-Op
        # try:
        #     logger.info(f"Joining channel {name} {channel_id}")
        #     settings.SLACK_CLIENT.join_channel(channel_id)
        # except SlackError as e:
        #     logger.error(f"Failed to join comms channel {e}")
        #     raise


        meeting = self.create(
            incident=incident, weblink=weblink, challenge=challenge
        )
        return meeting


class Meeting(models.Model):

    objects = MeetingManager()
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE)
    channel_id = models.CharField(max_length=20, null=False)
    channel_name = models.CharField(max_length=80, null=False)


    def __str__(self):
        return self.weblink
