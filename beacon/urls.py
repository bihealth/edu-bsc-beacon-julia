from . import views
from django.urls import path

# The urlpatterns of the beacon endpoints
urlpatterns = [
    path("", views.CaseInfoEndpoint.as_view(), name="info"),
    path("query", views.CaseQueryEndpoint.as_view(), name="query"),
]
