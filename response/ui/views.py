import datetime
import os
from itertools import chain
from operator import attrgetter
import logging
import requests
from atlassian import Confluence
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.http import Http404, HttpRequest
from django.shortcuts import redirect, render
from django.template import loader
import html
from response.core.models import Action, Incident, StatusUpdate
from response.decorators import response_login_required
from response.slack.models import PinnedMessage, UserStats

logger = logging.getLogger(__name__)

@response_login_required
def home(request: HttpRequest):
    incidents = Incident.objects.all().order_by("-start_time")
    some_day_last_week = timezone.now().date() - timedelta(days=7)
    monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
    monday_of_this_week = monday_of_last_week + timedelta(days=7)
    incidents_last_week = Incident.objects.filter(report_time__gte=monday_of_last_week, report_time__lt=monday_of_this_week)
    incidents_this_week = Incident.objects.filter(report_time__gte=monday_of_this_week)
    return render(request, template_name="home.html", context={"incidents": incidents,"incidents_last_week": incidents_last_week, "incidents_this_week":incidents_this_week})


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
    if incident.impact is not None:
        content_file = content_file.replace("%IMPACT%", incident.impact)
    else:
        content_file = content_file.replace("%IMPACT%", '')
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
    if incident.summary is None:
        content_file = content_file.replace("%SUMMARY%", '')
    else:
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

        timeline_content += "<td>" + update + html.escape(item.text) + "</td>"
        timeline_content += "</tr>"

    content_file = content_file.replace("%TIMELINE%", timeline_content)
    s = requests.Session()
    s.headers["Authorization"] = "Bearer " + settings.CONFLUENCE_TOKEN
    b = Confluence(
        url=settings.CONFLUENCE_URL,
        username=settings.CONFLUENCE_USER,
        password=settings.CONFLUENCE_TOKEN,
    )

    logger.info(content_file)
    page_created = b.create_page(
        space=settings.CONFLUENCE_SPACE,
        title="["
        + incident.start_time.strftime("%Y-%m-%d")
        + "] PostMortem "
        + incident.report,
        body=content_file,
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
