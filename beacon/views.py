from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpRequest
from django.views import View
from Django.DB import models


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
        get method for info endpoint
        callable through "curl https://host/"
        :param request:
        :return: JSONResponse
        """


class CaseQueryEndpoint(View):

    def post(self, request, *args, **kwargs):
        """
        post method for query endpoint
        callable through: curl -d "referenceName=1&start=14929&referenceBases=A&alternateBases=G&key=password1234" https://localhost:5000/query
        :param request:
        :rtype: JSONResponse
        """

    def _process_query(self, request):
        """
        input: query string from request
        # RegisterForm
        checks if input is valid and assigns to variables

        :rtype: chr, pos, ref, alt
        """

    def _authenticate(self, key):
        """
        authenticate client by comparing key to consortium
        :rtype: visibility level
        """

    def _check_access_limit(self):
        """
        # logging in setting by file?
        :rtype: object
        """

    def _get_query_set(self, vis_level):
        """

        :rtype: array of query sets

        """