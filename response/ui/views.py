import datetime
import os
from itertools import chain
from operator import attrgetter
import logging
import html
import requests
from atlassian import Confluence
from django.conf import settings
from django.http import Http404, HttpRequest
from django.shortcuts import redirect, render
from django.template import loader

from response.core.models import Action, Incident, StatusUpdate
from response.decorators import response_login_required
from response.slack.models import PinnedMessage, UserStats

logger = logging.getLogger(__name__)

@response_login_required
def home(request: HttpRequest):
    incidents = Incident.objects.all().order_by("-start_time")
    return render(request, template_name="home.html", context={"incidents": incidents})


@response_login_required
def export_to_confluence(request: HttpRequest, incident_id: str):
    try:
        incident = Incident.objects.get(pk=incident_id)
    except Incident.DoesNotExist:
        raise Http404("Incident does not exist")

    module_dir = os.path.dirname(__file__)
    file_path = os.path.join(module_dir, "postmortem.html")  # full path to text.
    f = open(file_path, "r")
    content_file = f.read()
    content_file = content_file.replace("%SEVERITY%", incident.severity_text())
    content_file = content_file.replace("%IMPACT%", incident.impact)
    content_file = content_file.replace(
        "%START_TIME%", incident.start_time.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    )
    content_file = content_file.replace(
        "%END_TIME%", incident.end_time.strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    )
    content_file = content_file.replace(
        "%LINK%",
        "{0}://{1}{2}".format(request.scheme, request.get_host(), request.path).replace(
            "export", ""
        ),
    )
    content_file = content_file.replace("%SUMMARY%", incident.summary)

    events = PinnedMessage.objects.filter(incident=incident).order_by("timestamp")
    updates = StatusUpdate.objects.filter(incident=incident).order_by("timestamp")

    timeline_list = sorted(
        chain(events, updates), key=attrgetter("timestamp"), reverse=False
    )
    timeline_content = ""
    for item in timeline_list:
        update = ""
        print(item.__class__.__name__)
        if "StatusUpdate" in item.__class__.__name__:
            update = "UPDATE: "

        timeline_content += "<tr>"
        timeline_content += (
            "<td>" + item.timestamp.strftime("%Y-%m-%d %H:%M:%S") + " UTC" + "</td>"
        )

        timeline_content += "<td>" + update + item.text + "</td>"
        timeline_content += "</tr>"

    content_file = content_file.replace("%TIMELINE%", timeline_content)
    s = requests.Session()
    s.headers["Authorization"] = "Bearer " + settings.CONFLUENCE_TOKEN
    b = Confluence(
        url=settings.CONFLUENCE_URL,
        username=settings.CONFLUENCE_USER,
        password=settings.CONFLUENCE_TOKEN,
    )
    logger.info(settings.CONFLUENCE_SPACE)
    logger.info("["
        + incident.start_time.strftime("%Y-%m-%d")
        + "] PostMortem "
        + incident.report)
    logger.info(html.escape(content_file))
    page_created = b.create_page(
        space=settings.CONFLUENCE_SPACE,
        title="["
        + incident.start_time.strftime("%Y-%m-%d")
        + "] PostMortem "
        + incident.report,
        body=html.escape(content_file),
        parent_id=settings.CONFLUENCE_PARENT,
    )
    links_data = page_created["_links"]

    incident.post_mortem = links_data["base"] + links_data["webui"]
    incident.save()
    return redirect("incident_doc", incident_id=incident_id)


@response_login_required
def incident_doc(request: HttpRequest, incident_id: str):
    try:
        incident = Incident.objects.get(pk=incident_id)
    except Incident.DoesNotExist:
        raise Http404("Incident does not exist")

    events = PinnedMessage.objects.filter(incident=incident).order_by("-timestamp")
    actions = Action.objects.filter(incident=incident).order_by("created_date")
    updates = StatusUpdate.objects.filter(incident=incident).order_by("-timestamp")
    user_stats = UserStats.objects.filter(incident=incident).order_by("-message_count")[
        :5
    ]
    confluence = settings.EXPORT_CONFLUENCE
    return render(
        request,
        template_name="incident_doc.html",
        context={
            "incident": incident,
            "events": events,
            "updates": updates,
            "actions": actions,
            "user_stats": user_stats,
            "confluence": confluence,
        },
    )
