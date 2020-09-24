from django.apps import AppConfig
from django.conf import settings as site_settings


class ResponseConfig(AppConfig):
    name = "response"

    def ready(self):
        from .core import signals as core_signals  # noqa: F401
        from .slack import (  # noqa: F401
            action_handlers,
            dialog_handlers,
            event_handlers,
            incident_commands,
            incident_notifications,
            settings,
            signals,
        )

        site_settings.RESPONSE_LOGIN_REQUIRED = getattr(
            site_settings, "RESPONSE_LOGIN_REQUIRED", True
        )
