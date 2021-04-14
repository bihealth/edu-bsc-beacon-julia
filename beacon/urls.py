from . import views
from django.urls import path

urlpatterns = [
    path('', views.CaseInfoEndpoint.as_view()),
    path('query', views.CaseQueryEndpoint.as_view())
]
