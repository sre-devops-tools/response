import logging
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from response.core.models import Action, ExternalUser, Incident, StatusUpdate
from response.slack.block_kit import (Actions, Button, Divider, Message,
                                      Section, Text)
from response.slack.cache import get_user_profile, get_user_profile_by_name
from response.slack.client import SlackError
from response.slack.decorators.incident_command import (
    __default_incident_command, get_help)
from response.slack.models import CommsChannel, HeadlinePost
from response.slack.reference_utils import reference_to_id
from response.zoom.models import Meeting
from response.zoom.zoom import Zoom

logger = logging.getLogger(__name__)


@__default_incident_command(["help"], helptext="` - Display a list of commands and usage")
def send_help_text(incident: Incident, user_id: str, message: str):
    return True, get_help()


@__default_incident_command(
    ["update"], helptext="[text]` - Provide an update about the status of the incident"
)
def add_status_update(incident: Incident, user_id: str, message: str):
    name = get_user_profile(user_id)["name"]
    action_reporter, _ = ExternalUser.objects.get_or_create_slack(
        external_id=user_id, display_name=name
    )
    StatusUpdate(incident=incident, text=message, user=action_reporter).save()
    msg = Message()
    msg.add_block(
        Section(
            block_id="update",
            text=Text(f":warning: *Update:*\n{message} "),
        )
    )
    comms_channel = CommsChannel.objects.get(incident=incident)
    ts = HeadlinePost.objects.get(incident=incident).message_ts
    msg.send(comms_channel.channel_id, None)
    settings.SLACK_CLIENT.send_message(
        settings.INCIDENT_CHANNEL_ID, ":warning: *Update*: " + message, thread_ts=ts
    )

    # comms_channel.post_in_channel(msg)
    return True, None


@__default_incident_command(["lead"], helptext="[@user]` - Assign someone as the incident lead")
def set_incident_lead(incident: Incident, user_id: str, message: str):
    assignee = get_user_profile_by_name(message)

    name = assignee['name']
    print(name)
    user, _ = ExternalUser.objects.get_or_create_slack(
        external_id=assignee['id'], display_name=name
    )
    incident.lead = user
    incident.save()
    return add_status_update(incident, user_id,'New lead is '+incident.lead.full_name)


@__default_incident_command(["severity"], helptext="[critical|major|minor|trivial]` - Set the incident severity")
def set_severity(incident: Incident, user_id: str, message: str):
    for sev_id, sev_name in Incident.SEVERITIES:
        # look for sev name (e.g. critical) or sev id (1)
        if (sev_name in message.lower()) or (sev_id in message.lower()):
            incident.severity = sev_id
            incident.save()
            return add_status_update(incident, user_id,'Severity updated to '+incident.severity_text())

    return False, None


@__default_incident_command(["rename"], helptext="[text]` - Rename the incident channel")
def rename_incident(incident: Incident, user_id: str, message: str):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        logger.info(f"Renaming channel to {message}")
        comms_channel.rename(message)
    except SlackError:
        return (
            True,
            "👋 Sorry, the channel couldn't be renamed. Make sure that name isn't taken already and it's not too long.",
        )
    return True, None


@__default_incident_command(
    ["duration"], helptext="` - How long has this incident been running?"
)
def set_duration(incident: Incident, user_id: str, message: str):
    duration = incident.duration()

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(f"The incident has been running for {duration}")

    return True, None


@__default_incident_command(["close"], helptext="` - Close this incident.")
def close_incident(incident: Incident, user_id: str, message: str):
    comms_channel = CommsChannel.objects.get(incident=incident)

    if incident.is_closed():
        comms_channel.post_in_channel(
            f"This incident was already closed at {incident.end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return True, None

    incident.end_time = datetime.now()
    incident.save()

    comms_channel.post_in_channel("This incident has been closed! 📖 ⟶ 📕")

    return True, None


@__default_incident_command(["action"], helptext="[text]` - Log a follow up action")
def set_action(incident: Incident, user_id: str, message: str):
    name = get_user_profile(user_id)["name"]
    action_reporter, _ = ExternalUser.objects.get_or_create_slack(
        external_id=user_id, display_name=name
    )
    Action(incident=incident, details=message, user=action_reporter).save()
    return True, None


@__default_incident_command(["zoom"], helptext="` - Creates a zoom meeting")
def create_zoom(incident: Incident, user_id: str, message: str):
    try:
        m = incident.zoom_meeting()
    except ObjectDoesNotExist:
        m = Meeting.objects.create_meeting(incident)
        # Update the headline post here too
        h = HeadlinePost.objects.get(incident=incident)
        h.zoom_meeting = m
        h.save()
        h.update_in_slack()

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(
        f"You can join the zoom meeting here {m.weblink} with password `{m.challenge}`"
    )

    return True, None

@__default_incident_command(['mitigate'], helptext="[message]` - Change the status of the incident to mitigated")
def mitigate_incident(incident: Incident, user_id: str, message: str):
    incident.mitigated = True
    incident.save()
    return add_status_update(incident, user_id,'Status changed to Mitigated - '+ message)

