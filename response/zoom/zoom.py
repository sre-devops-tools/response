import logging
import random
from typing import List

from .client import ZoomClient
from .settings import ZOOM_API_KEY, ZOOM_API_SECRET, ZOOM_API_USER_ID


log = logging.getLogger(__name__)


def gen_conference_challenge(length: int):
    """Generate a random challenge for Zoom."""
    if length > 10:
        length = 10
    field = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.sample(field, length))


def delete_meeting(client, event_id: int):
    return client.delete("/meetings/{}".format(event_id))


def create_meeting(
    client,
    name: str,
    description: str = None,
    title: str = None,
    duration: int = 60000,  # duration in mins ~6 weeks
):
    """Create a Zoom Meeting."""
    body = {
        "topic": title if title else f"Situation Room for {name}",
        "agenda": description
        if description
        else f"Situation Room for {name}. Please join.",
        "duration": duration,
        "password": gen_conference_challenge(8),
        "settings": {"join_before_host": True},
    }

    return client.post("/users/{}/meetings".format(ZOOM_API_USER_ID), data=body)


class Zoom:
    def __init__(self):
        self.client = ZoomClient(ZOOM_API_KEY, ZOOM_API_SECRET)

    def create(
        self,
        name: str,
        description: str = None,
        title: str = None,
        participants: List[str] = [],
    ):
        """Create a new event."""

        conference_response = create_meeting(
            self.client, name, description=description, title=title
        )

        conference_json = conference_response.json()

        return {
            "weblink": conference_json.get("join_url", "https://zoom.us"),
            "id": conference_json.get("id", "1"),
            "challenge": conference_json.get("password", "123"),
        }
