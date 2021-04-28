from django.http import JsonResponse
from django.views import View
import re
from .models import (
    Variant,
    RemoteSite,
    Consortium,
    LogEntry,
    MetadataBeacon,
    MetadataBeaconOrganization,
    MetadataBeaconDataset,
)
from .json_structures import AlleleRequest, AlleleResponse, Error, InfoResponse, DatasetResponse, OrganizationResponse, \
    QueryResponse
from .queries import CaseQueryVariant
from datetime import datetime, date


class CaseInfoEndpoint(View):

    def get(self, request, *args, **kwargs):
        """
        get method for info endpoint
        callable through "curl https://host/"
        :param request:
        :return: JSONResponse
        """
        return self._handle(request, *args, **kwargs)

    def _handle(self, request, *args, **kwargs):
        metadata_beacon = MetadataBeacon.objects.all()
        datasets = MetadataBeaconDataset.objects.filter(metadata_beacon=metadata_beacon[0])
        datasets_dict_list = []
        for d in datasets:
            datasets_dict = DatasetResponse(d.beacon_data_id,
                                            d.name,
                                            d.assembly_id,
                                            d.create_date_time,
                                            d.update_date_time).create_dict()
            datasets_dict_list.append(datasets_dict)
        organisations = MetadataBeaconOrganization.objects.filter(metadata_beacon=metadata_beacon[0])
        dict_org = OrganizationResponse(organisations[0].beacon_org_id,
                                        organisations[0].name,
                                        organisations[0].contact_url).create_dict()
        output = JsonResponse(
            InfoResponse(metadata_beacon[0].beacon_id, metadata_beacon[0].name, metadata_beacon[0].api_version,
                         datasets_dict_list, dict_org).create_dict(), json_dumps_params={'indent': 2})
        LogEntry(ip_address=request.META.get('REMOTE_ADDR'),
                 user_identifier=request.META.get('USER'),
                 authuser=RemoteSite.objects.get(name='public'),
                 date_time=datetime.now(),
                 request=("%s %s %s" % (request.method, request.body, request.META["SERVER_PROTOCOL"])),
                 status_code=output.status_code,
                 response_size=len(output.content)).save()
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
        return self._handle(request, chromosome, start, end, reference, alternative, release)

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
        return self._handle(request, chromosome, start, end, reference, alternative, release)

    def _handle(self, request, chromosome, start, end, reference, alternative, release):
        try:
            if release is None:
                release = "GRCh37"
            allele_request = AlleleRequest(chromosome, start, end, reference, alternative, release).create_dict()
            beacon_id, api_version = self._query_metadata()
            output_json = QueryResponse(beacon_id, api_version, allele_request).create_dict()
            if self._check_query_input(chromosome, start, end, reference, alternative):
                output_json["error"] = Error(400, "The input format is invalid.").create_dict()
                raise UnboundLocalError()
            if "Authorization" in request.headers:
                key = request.headers["Authorization"]
            else:
                key = "public"
            remote_site = self._authenticate(key)
            if not list(remote_site):
                output_json["error"] = Error(401, "You are not authorized as a user.").create_dict()
                raise UnboundLocalError()
            if self._check_access_limit(remote_site[0]):
                output_json["error"] = Error(403, "You have exceeded your access limit.").create_dict()
                raise UnboundLocalError()
            query_parameters = self._query_variant(remote_site[0].consortia,
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
        except UnboundLocalError:  # Not authenticated or invalid arguments
            output = JsonResponse(output_json, status=output_json["error"]["errorCode"],
                                  json_dumps_params={'indent': 2})
        LogEntry(ip_address=request.META.get('REMOTE_ADDR'),
                 user_identifier=request.META.get('USER'),
                 authuser=remote_site[0],
                 date_time=datetime.now(),
                 request=("%s %s %s" % (request.method, request.body, request.META["SERVER_PROTOCOL"])),
                 status_code=output.status_code,
                 response_size=len(output.content)).save()
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
        remote_site = RemoteSite.objects.filter(key=key)
        return remote_site

    def _check_access_limit(self, remote_site):
        """
        # logging in setting by file?
        :rtype: object
        """
        access_limit = remote_site.access_limit
        if LogEntry.objects.filter(authuser=remote_site, date_time__contains=date.today()).count() > access_limit:
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
                                          case__project__consortium__in=consortium.all()).distinct()
        for v in variants:
            variant_query.exists = True
            visibility_level = self._get_highest_vis_level(v.case.project, consortium)
            if visibility_level == 20:
                variant_query.make_query_20(v)
            if visibility_level == 15:
                variant_query.make_query_15(v)
            if visibility_level == 10:
                variant_query.make_query_10(v)
            if visibility_level == 5:
                variant_query.make_query_5(v)
            if visibility_level == 0:
                variant_query.make_query_0(v)
        return AlleleResponse(variant_query.exists,
                              variant_query.allele_count_greater_ten,
                              variant_query.allele_count,
                              variant_query.coarse_phenotypes,
                              variant_query.phenotypes,
                              variant_query.case_indices)

    def _query_metadata(self):
        metadata_beacon = MetadataBeacon.objects.all()
        return metadata_beacon[0].beacon_id, metadata_beacon[0].api_version

    def _get_highest_vis_level(self, projects, consortium):
        consortia = Consortium.objects.filter(projects=projects, id__in=consortium.all().values("id")).values(
            "visibility_level")
        return min([c["visibility_level"] for c in consortia])
