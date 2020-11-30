from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("incident/<int:incident_id>/", views.incident_doc, name="incident_doc"),
    path(
        "incident/<int:incident_id>/export", views.export_to_confluence, name="export"
    ),
]
