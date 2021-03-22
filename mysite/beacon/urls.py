from django.urls import path
from . import views
from .views import CaseInfoEndpoint, CaseQueryEndpoint

urlpatterns = [
    path('/', views.CaseInfoEndpoint.as_view(), name='info'),
    path('/query', views.CaseQueryEndpoint.as_view(), name='query')
]