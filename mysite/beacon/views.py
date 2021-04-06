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
from datetime import datetime, date


class CaseInfoEndpoint(View):

    def get(self, request, *args, **kwargs):
        """
        get method for info endpoint
        callable through "curl https://host/"
        :param request:
        :return: JSONResponse
        """
        # try:
       # with request as r:
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
        ## if cant fecht client adress
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
        try:
            chromosome = request.GET.get("referenceName")
            start = request.GET.get("start")
            end = request.GET.get("end")
            reference = request.GET.get("referenceBases")
            alternative = request.GET.get("alternateBases")
            release = request.GET.get("assemblyId")
            if release is None:
                release = "GRCh37"
            beacon_id, api_version = self._query_metadata()
            allele_request = AlleleRequest(chromosome, start, end, reference, alternative, release).create_dict()
            output_json = {"beaconId": beacon_id, "apiVersion": api_version, "exists": None,
                           "error": None, "alleleRequest": allele_request, "datasetAlleleResponses": []}
            if self._check_query_input(chromosome, start, end, reference, alternative):
                output_json["error"] = {"errorCode": 400, "errorMessage": "The input format is invalid."}
                output = JsonResponse(output_json, status=400, json_dumps_params={'indent': 2})
                raise UnboundLocalError()
            if "Authorization" in request.headers:
                key = request.headers["Authorization"]
            else:
                key = "public"
            print(key)
            remote_side = self._authenticate(key)
            if not list(remote_side):
                output_json["error"] = {"errorCode": 401, "errorMessage": "You are not authorized as a user."}
                output = JsonResponse(output_json, status=401, json_dumps_params={'indent': 2})
                raise UnboundLocalError()
            if self._check_access_limit(remote_side[0]):
                output_json["error"] = {"errorCode": 403, "errorMessage": "You have exceeded your access limit."}
                output = JsonResponse(output_json, status=403, json_dumps_params={'indent': 2})
                raise UnboundLocalError()
            query_parameters = self._query_variant(remote_side[0].consortium,
                                                   chromosome,
                                                   start,
                                                   end,
                                                   reference,
                                                   alternative,
                                                   release)
            if query_parameters.exists is False:
                output_json["exists"] = False
            else:
                output_json["exists"] = True
                output_json["datasetAlleleResponses"] = query_parameters.create_dict()
            output = JsonResponse(output_json, json_dumps_params={'indent': 2})
            log_entry = LogEntry(ip_address=request.META.get('REMOTE_ADDR'),
                                 user_identifier=request.META.get('USER'),
                                 authuser=remote_side[0], date_time=datetime.now(),
                                 request=("%s %s %s" % (
                                     request.method, request.body, request.META["SERVER_PROTOCOL"])),
                                 status_code=output.status_code,
                                 response_size=len(output.content)
                                 )
            log_entry.save()
            return JsonResponse(output_json, json_dumps_params={'indent': 2})
        except UnboundLocalError:
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
        if self._check_access_limit(remote_side[0]):
            return HttpResponse('Unauthorized', status=401)
        allele_request = AlleleRequest(chromosome, start, end, reference, alternative, release).create_dict()
        query_parameters = self._query_variant(remote_side[0].consortium, chromosome, start, end, reference,
                                               alternative,
                                               release)
        if query_parameters.exists is False:
            output_json = {"beaconId": beacon_id, "apiVersion": api_version, "exists": query_parameters[0],
                           "error": None, "alleleRequest": allele_request, "datasetAlleleResponses": []}
        else:
            output_json = {"beaconId": beacon_id, "apiVersion": api_version, "exists": query_parameters.exists,
                           "error": None, "alleleRequest": allele_request, "datasetAlleleResponses": query_parameters.create_dict()}
        output = JsonResponse(output_json, json_dumps_params={'indent': 2})
        log_entry = LogEntry(ip_address=request.META.get('REMOTE_ADDR'),
                             user_identifier=request.META.get('USER'),
                             authuser=remote_side[0], date_time=datetime.now(),
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
        if LogEntry.objects.filter(authuser=remote_side, date_time__contains=date.today()).count() > access_limit:
            return True
        else:
            return False

    def _query_variant(self, consortium, chromosome, start, end, reference, alternative, release):
        """

        :rtype: array of query sets

        """
        variant_query = CaseQueryVariant()
        variants = Variant.objects.filter(chromosome=chromosome,
                                          start=start,
                                          reference=reference,
                                          end=end,
                                          alternative=alternative,
                                          release=release,
                                          case__project__consortium__in=consortium.all())
        for v in variants:
            variant_query.exists = True
            visibility_level = self._get_highest_vis_level(v.case.project)
            if visibility_level == "20":
                variant_query.make_query_20(v)
            elif visibility_level == "15":
                variant_query.make_query_15(v)
            elif visibility_level == "10":
                variant_query.make_query_10(v)
            elif visibility_level == "5":
                variant_query.make_query_5(v)
            else:
                variant_query.make_query_0(v)
        return AlleleResponse(variant_query.exists,
                              variant_query.allele_count_greater_ten,
                              variant_query.allele_count,
                              variant_query.coarse_phenotypes,
                              variant_query.phenotypes,
                              variant_query.case_indices)

    def _query_metadata(self):
        try:
            beacons = MetadataBeacon.objects.all()
            beacon_id = beacons[0].beacon_id
            api_version = beacons[0].api_version
            return beacon_id, api_version
        except ValueError:
            return 0

    def _get_highest_vis_level(self, project):
        consortia = Consortium.objects.filter(projects=project).values("visibility_level")
        return min([c["visibility_level"] for c in consortia])
