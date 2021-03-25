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
    Consortium,
    MetadataBeacon,
    MetadataBeaconOrganization,
    MetadataBeaconDataset,
)
from .json_structures import AlleleRequest, AlleleResponse


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
        # except IndexError:
        return JsonResponse(output_json, json_dumps_params={'indent': 2})


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
        if self._check_query_input(chromosome, start, end, reference, alternative):
            return HttpResponseBadRequest("Bad request: The input format is invalid.")
        if "Authorization" in request.headers:
            key = request.headers["Authorization"]
        else:
            key = "public"
        consortium = self._authenticate(key)
        if not list(consortium):
            return HttpResponse('Unauthorized', status=401)
        # if self._check_access_limit():
        allele_request = AlleleRequest(chromosome, start, end, reference, alternative).create_dict()
        query_parameters = self._query_variant(consortium[0], chromosome, start, end, reference, alternative)
        allele_response = AlleleResponse(query_parameters[0], query_parameters[1], query_parameters[2], query_parameters[3], query_parameters[4]).create_dict()
        output_json = {"alleleRequest": allele_request, "datasetAlleleResponses": allele_response}
        return JsonResponse(output_json, json_dumps_params={'indent': 2})

    def post(self, request, *args, **kwargs):
        """
        post method for query endpoint
        curl -d "referenceName=1&start=14929&end=15000&referenceBases=A&alternateBases=G" -H "Authorization: xxxxxxxx" -X POST http://localhost:3000/data
        :param request:
        :rtype: JSONResponse
        """
        chromosome = request.POST.get("referenceName")
        start = request.POST.get("start")
        end = request.POST.get("end")
        reference = request.POST.get("referenceBases")
        alternative = request.POST.get("alternateBases")
        if self._check_query_input(chromosome, start, end, reference, alternative):
            return HttpResponseBadRequest("Bad request: The input format is invalid.")
        if "Authorization" in request.headers:
            key = request.headers["Authorization"]
        else:
            key = "public"
        consortium = self._authenticate(key)
        if not list(consortium):
            return HttpResponse('Unauthorized', status=401)
        # if self._check_access_limit():
        allele_request = AlleleRequest(chromosome, start, end, reference, alternative).create_dict()
        query_parameters = self._query_variant(consortium[0], chromosome, start, end, reference, alternative)
        allele_response = AlleleResponse(query_parameters[0], query_parameters[1], query_parameters[2], query_parameters[3], query_parameters[4]).create_dict()
        output_json = {"alleleRequest": allele_request, "datasetAlleleResponses": allele_response}
        return JsonResponse(output_json, json_dumps_params={'indent': 2})


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
        consortium = Consortium.objects.filter(key=key)
        return consortium

    def _check_access_limit(self, consortium_pk):
        """
        # logging in setting by file?
        :rtype: object
        """
        return 0

    def _query_variant(self, consortium, chromosome, start, end, reference, alternative):
        """

        :rtype: array of query sets

        """
        variants = Variant.objects.filter(chromosome=chromosome, start=start, reference=reference, end=end,
                                          alternative=alternative, case_id__project__consortium=consortium.id).select_related("case_id__project__consortium").values("id", "case_id")
        print(variants)
        if not list(variants):
            return False, None, None, None, None
        if consortium.visibility_level == "25":
            return True, None, None, None, None
        if consortium.visibility_level == "20":
            if len(variants) > 10:
                return True, True, None, None, None
            else:
                return True, False, None, None, None
        if consortium.visibility_level == "15":
            allele_count = len(variants)
            if allele_count > 10:
                return True, True, allele_count, None, None
            else:
                return True, False, allele_count, None, None
        if consortium.visibility_level == "10":
            allele_count = len(variants)
            phenotypes = []
            for p in Phenotype.objects.filter(case_id=variants[0]["case_id"]):
                phenotypes.append(p.phenotype)
            coarse_phenotypes = []
            # for p in phenotypes: coarse_phenotype.append(p.get_coarse_phenotype())
            if allele_count > 10:
                return True, True, allele_count, coarse_phenotypes, None
            else:
                return True, False, allele_count, coarse_phenotypes, None
        if consortium.visibility_level == "5":
            allele_count = len(variants)
            phenotypes = []
            for p in Phenotype.objects.filter(case_id=variants[0]["case_id"]):
                phenotypes.append(p.phenotype)
            coarse_phenotypes = []
            # for p in phenotypes: coarse_phenotype.append(p.get_coarse_phenotype())
            if allele_count > 10:
                return True, True, allele_count, coarse_phenotypes, phenotypes
            else:
                return True, False, allele_count, coarse_phenotypes, phenotypes
        return 0
