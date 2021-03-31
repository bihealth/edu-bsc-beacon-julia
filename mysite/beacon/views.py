from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse, HttpResponseBadRequest
from django.views import View
from django.db import models
import re
from .models import (
    Variant,
    Phenotype,
    Case,
    Project,
    RemoteSide,
    Consortium,
    LogEntry,
    MetadataBeacon,
    MetadataBeaconOrganization,
    MetadataBeaconDataset,
)
from .json_structures import AlleleRequest, AlleleResponse
from .queries import (CaseQueryVariant)
from datetime import datetime


class CaseInfoEndpoint(View):

    def get(self, request, *args, **kwargs):
        """
        get method for info endpoint
        callable through "curl https://host/"
        :param request:
        :return: JSONResponse
        """
        # try:
        beacons = MetadataBeacon.objects.all()
        beacon_id = beacons[0].beacon_id
        name = beacons[0].name
        api_version = beacons[0].api_version
        output_json = {"beaconID": beacon_id,
                       "name": name,
                       "apiVersion": api_version}
        datasets = MetadataBeaconDataset.objects.filter(beacon_id=beacon_id)
        datasets_dict_list = []
        for d in datasets:
            beacon_data_id = d.beacon_data_id
            data_name = d.name
            assembly_id = d.assembly_id
            create_date_time = d.create_date_time
            update_date_time = d.update_date_time
            datasets_dict = {"id": beacon_data_id,
                             "name": data_name,
                             "assemblyId": assembly_id,
                             "createDateTime": create_date_time,
                             "updateDateTime": update_date_time,
                             }
            datasets_dict_list.append(datasets_dict)
        output_json["dataset"] = datasets_dict_list
        organisations = MetadataBeaconOrganization.objects.filter(beacon_id=beacon_id)
        org_id = organisations[0].beacon_org_id
        org_name = organisations[0].name
        contact_url = organisations[0].contact_url
        dict_org = {"id": org_id,
                    "name": org_name,
                    "contactURL": contact_url
                    }
        output_json["organization"] = dict_org
        output = JsonResponse(output_json, json_dumps_params={'indent': 2})
        log_entry = LogEntry(ip_address=request.META.get('REMOTE_ADDR'),
                             user_identifier=request.META.get('USER'),
                             authuser=Consortium.objects.get(name='public'), date_time=datetime.now(),
                             request=("%s %s %s" % (
                                 request.method, request.get_full_path(), request.META["SERVER_PROTOCOL"])),
                             status_code=output.status_code,
                             response_size=len(output.content)
                             )
        log_entry.save()
        return output


class CaseQueryEndpoint(View):

    def get(self, request, *args, **kwargs):
        """
        get method for query endpoint
        callable through: curl -H "Authorization: xxxxxxxx"
        https://localhost:5000/query?referenceName=1&start=14929&end=15000&referenceBases=A&alternateBases=G&key=password1234"
        :param request:
        :rtype: JSONResponse
        """
        chromosome = request.GET.get("referenceName")
        start = request.GET.get("start")
        end = request.GET.get("end")
        reference = request.GET.get("referenceBases")
        alternative = request.GET.get("alternateBases")
        release = request.GET.get("assemblyId")
        if release is None:
            release = "GRCh37"
        beacon_id, api_version = self._query_metadata()
        if self._check_query_input(chromosome, start, end, reference, alternative):
            return HttpResponseBadRequest("Bad request: The input format is invalid.")
        if "Authorization" in request.headers:
            key = request.headers["Authorization"]
        else:
            key = "public"
        remote_side = self._authenticate(key)
        if not list(remote_side):
            return HttpResponse('Unauthorized', status=401)
        # if self._check_access_limit():
        allele_request = AlleleRequest(chromosome, start, end, reference, alternative, release).create_dict()
        query_parameters = self._query_variant(remote_side[0].consortium, chromosome, start, end, reference, alternative,
                                               release)
        if query_parameters[0] is False:
            output_json = {"beaconId": beacon_id,
                           "apiVersion": api_version,
                           "exists": query_parameters[0],
                           "error": None,
                           "alleleRequest": allele_request,
                           "datasetAlleleResponses": []
                           }
        else:
            allele_response = AlleleResponse(query_parameters[0], query_parameters[1], query_parameters[2],
                                             query_parameters[3], query_parameters[4]).create_dict()
            output_json = {"beaconId": beacon_id,
                           "apiVersion": api_version,
                           "exists": query_parameters[0],
                           "error": None, "alleleRequest": allele_request,
                           "datasetAlleleResponses": allele_response
                           }

        output = JsonResponse(output_json, json_dumps_params={'indent': 2})
        log_entry = LogEntry(ip_address=request.META.get('REMOTE_ADDR'),
                             user_identifier=request.META.get('USER'),
                             authuser=consortium[0], date_time=datetime.now(),
                             request=("%s %s %s" % (
                                 request.method, request.get_full_path(), request.META["SERVER_PROTOCOL"])),
                             status_code=output.status_code,
                             response_size=len(output.content)
                             )
        log_entry.save()
        return output

    def post(self, request, *args, **kwargs):
        """
        post method for query endpoint
        curl -d "referenceName=1&start=14929&end=15000&referenceBases=A&alternateBases=G&assemblyId=GRCh37" -H "Authorization: xxxxxxxx" -X POST http://localhost:3000/data
        :param request:
        :rtype: JSONResponse
        """
        chromosome = request.POST.get("referenceName")
        start = request.POST.get("start")
        end = request.POST.get("end")
        reference = request.POST.get("referenceBases")
        alternative = request.POST.get("alternateBases")
        release = request.POST.get("assemblyId")
        if release is None:
            release = "GRCh37"
        beacon_id, api_version = self._query_metadata()
        if self._check_query_input(chromosome, start, end, reference, alternative):
            return HttpResponseBadRequest("Bad request: The input format is invalid.")
        if "Authorization" in request.headers:
            key = request.headers["Authorization"]
        else:
            key = "public"
        remote_side = self._authenticate(key)
        if not list(remote_side):
            return HttpResponse('Unauthorized', status=401)
        # if self._check_access_limit():
        allele_request = AlleleRequest(chromosome, start, end, reference, alternative, release).create_dict()
        query_parameters = self._query_variant(remote_side[0].consortium, chromosome, start, end, reference, alternative,
                                               release)
        if query_parameters["exists"] is False:
            output_json = {"beaconId": beacon_id, "apiVersion": api_version, "exists": query_parameters[0],
                           "error": None, "alleleRequest": allele_request, "datasetAlleleResponses": []}
        else:
            output_json = {"beaconId": beacon_id, "apiVersion": api_version, "exists": query_parameters[0],
                           "error": None, "alleleRequest": allele_request, "datasetAlleleResponses": query_parameters}
        output = JsonResponse(output_json, json_dumps_params={'indent': 2})
        log_entry = LogEntry(ip_address=request.META.get('REMOTE_ADDR'),
                             user_identifier=request.META.get('USER'),
                             authuser=consortium[0], date_time=datetime.now(),
                             request=("%s %s %s" % (
                                 request.method, request.body, request.META["SERVER_PROTOCOL"])),
                             status_code=output.status_code,
                             response_size=len(output.content)
                             )
        log_entry.save()
        return output

    def _check_query_input(self, chromosome, start, end, reference, alternative):
        """
        input: query string from request
        # RegisterForm
        checks if input is valid and assigns to variables

        :rtype: bool False if input is correct, true
        """
        chromosome_pattern = re.compile(r"[1-9]|[1][0-9]|[2][0-2]|[XY]")
        start_pattern = re.compile(r"(\d+)")
        end_pattern = re.compile(r"(\d+)")
        reference_pattern = re.compile(r"[ACGT]+")
        alternative_pattern = re.compile(r"[ACGT]+")
        try:
            if re.fullmatch(chromosome_pattern, chromosome) is None:
                return 1
            if re.fullmatch(start_pattern, start) is None:
                return 1
            if re.fullmatch(end_pattern, end) is None:
                return 1
            if re.fullmatch(reference_pattern, reference) is None:
                return 1
            if re.fullmatch(alternative_pattern, alternative) is None:
                return 1
        except TypeError:
            return 1
        return 0

    def _authenticate(self, key):
        """
        authenticate client by comparing key to consortium
        :rtype: bool
        """
        remote_side = RemoteSide.objects.filter(key=key)
        return remote_side

    def _check_access_limit(self, remote_side):
        """
        # logging in setting by file?
        :rtype: object
        """
        access_limit = remote_side.access_limit
        # if LogEntry.objects.filter(frank=consortium)
        return 0

    def _query_variant(self, consortium, chromosome, start, end, reference, alternative, release):
        """

        :rtype: array of query sets

        """
        consortium_dict = {}
        for c in consortium:
            if c.visibility_level == "25":
                consortium_dict[c.name] = CaseQueryVariant.make_query_25(consortium.id,
                                                                         chromosome,
                                                                         start,
                                                                         end,
                                                                         reference,
                                                                         alternative,
                                                                         release)
            elif c.visibility_level == "20":
                consortium_dict[c.name] = CaseQueryVariant.make_query_20(consortium.id,
                                                                         chromosome,
                                                                         start,
                                                                         end,
                                                                         reference,
                                                                         alternative,
                                                                         release)
            elif c.visibility_level == "15":
                consortium_dict[c.name] = CaseQueryVariant.make_query_15(consortium.id,
                                                                         chromosome,
                                                                         start,
                                                                         end,
                                                                         reference,
                                                                         alternative,
                                                                         release)
            elif c.visibility_level == "10":
                consortium_dict[c.name] = CaseQueryVariant.make_query_10(consortium.id,
                                                                         chromosome,
                                                                         start,
                                                                         end,
                                                                         reference,
                                                                         alternative,
                                                                         release)
            elif c.visibility_level == "5":
                consortium_dict[c.name] = CaseQueryVariant.make_query_5(consortium.id,
                                                                        chromosome,
                                                                        start,
                                                                        end,
                                                                        reference,
                                                                        alternative,
                                                                        release)
            else:
                consortium_dict[c.name] = CaseQueryVariant.make_query_0(consortium.id,
                                                                        chromosome,
                                                                        start,
                                                                        end,
                                                                        reference,
                                                                        alternative,
                                                                        release)
        return consortium_dict

    def _query_metadata(self):
        try:
            beacons = MetadataBeacon.objects.all()
            beacon_id = beacons[0].beacon_id
            api_version = beacons[0].api_version
            return beacon_id, api_version
        except ValueError:
            return 0
