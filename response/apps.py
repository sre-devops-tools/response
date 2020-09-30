from django.apps import AppConfig
from django.conf import settings as site_settings


class ResponseConfig(AppConfig):
    name = "response"

    def ready(self):
        from .core import signals as core_signals  # noqa: F401
        from .slack import (action_handlers, dialog_handlers,  # noqa: F401
                            event_handlers, incident_commands,
                            incident_notifications, settings, signals, updater)

        site_settings.RESPONSE_LOGIN_REQUIRED = getattr(
            site_settings, "RESPONSE_LOGIN_REQUIRED", True
        )

        updater.start()