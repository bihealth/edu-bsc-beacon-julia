from . import views
from django.urls import path

urlpatterns = [
    path(r'^/?$', views.CaseInfoEndpoint.as_view()),
    path(r'^query/?$', views.CaseQueryEndpoint.as_view())
]
