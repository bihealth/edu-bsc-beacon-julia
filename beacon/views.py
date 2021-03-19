from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpRequest
from django.views import View

from .models import (
    Variant,
    Phenotype,
    Case,
    Project,
    Consortium,
    ProjectConsortium,
    MetadataBeacon,
    MetadataBeaconOrganisation,
    MetadataBeaconDataset,
)


class CaseInfoEndpoint(View):
    def get(self, request, *args, **kwargs):
        """

        :rtype: JSONResponse
        """


class CaseQueryEndpoint(View):

    def post(self, request, *args, **kwargs):
        """

        :rtype: JSONResponse
        """

    def _process_query(self, query):
        """
        input: query string from request
        checks if input is valid

        :rtype: chr, pos, ref, alt
        """

    def _authenticate(self, key):
        """
        authenticate client by comparing key to consortium
        :rtype: bool permission, visibility level
        """

    def _get_filter(self, vis_level):
        """

        :rtype: object
        """

    def _check_access_limit(self):
        """

        :rtype: object
        """
