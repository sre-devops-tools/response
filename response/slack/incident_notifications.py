import logging
import datetime

from django.conf import settings
from response.core.models import Incident
from response.slack.decorators import recurring_notification
from response.slack.models import CommsChannel
from response.core.models import StatusUpdate

logger = logging.getLogger(__name__)

@recurring_notification(interval_mins=5, max_notifications=5)
def remind_severity(incident: Incident):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.severity:
            comms_channel.post_in_channel(
                "🌤️ This incident doesn't have a severity. Please set one with `@incident severity ...`"
            )
    except CommsChannel.DoesNotExist:
        pass


@recurring_notification(interval_mins=2, max_notifications=5)
def remind_incident_lead(incident: Incident):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.lead:
            comms_channel.post_in_channel(
                "👩‍🚒 This incident doesn't have a lead. Please set one with `@incident lead ...`"
            )
    except CommsChannel.DoesNotExist:
        pass

@recurring_notification(interval_mins=60, max_notifications=10)
def remind_update(incident: Incident):
    update = StatusUpdate.objects.filter(incident=incident).order_by("timestamp").first()
    if update is not None:
        if update.timestamp < datetime.datetime.now()-datetime.timedelta(minutes=60):
            logger.info("The last update is older than 60 minutes")
            try:
                comms_channel = CommsChannel.objects.get(incident=incident)
                if not incident.is_closed():
                    user_to_notify = incident.lead
                    settings.SLACK_CLIENT.send_ephemeral_message(
                        comms_channel.channel_id,
                        user_to_notify.external_id,
                        "The last update was over 1h ago. To provide a new update use the command:\n `/%s update [text]`"% settings.SLACK_SLASH_COMMAND,
            )
            except CommsChannel.DoesNotExist:
                pass

        else:
            logger.info("The last update is not older than 60 minutes")

@recurring_notification(interval_mins=1440, max_notifications=5)
def remind_close_incident(incident: Incident):

    # Only remind on weekdays (weekday returns an ordinal indexed from 0 on Monday)
    if datetime.datetime.now().weekday() in (5, 6):
        return

    # Only remind during the day to prevent alerting people at unsociable hours
    if datetime.datetime.now().hour not in range(9, 18):
        return

    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.is_closed():
            user_to_notify = incident.lead or incident.reporter
            comms_channel.post_in_channel(
                f":timer_clock: <@{user_to_notify.external_id}>, this incident has been running a long time."
                " Can it be closed now? Remember to pin important messages in order to create the timeline."
            )
    except CommsChannel.DoesNotExist:
        pass
