from . import views
from django.urls import path

urlpatterns = [
    path('', views.CaseInfoEndpoint.as_view(), name='info'),
    path('query', views.CaseQueryEndpoint.as_view(), name='query')
]
