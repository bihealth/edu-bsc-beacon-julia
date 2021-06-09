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
from .json_structures import (
    AlleleRequest,
    AlleleResponse,
    Error,
    InfoResponse,
    DatasetResponse,
    OrganizationResponse,
    QueryResponse,
)
from .queries import CaseQueryVariant
from datetime import date
from django.utils import timezone


class CaseInfoEndpoint(View):
    def get(self, request, *args, **kwargs):
        """
        GET method for beacon info endpoint

        :param request: A django HttpRequest object.
        :return: JSONResponse
        """
        return self._handle(request, *args, **kwargs)

    def _handle(self, request, *args, **kwargs):
        """
        Handles requests for beacon 'info' endpoint.

        :param request: A django HttpRequest object.
        :return: JSONResponse
        """
        # collect metadata from database
        metadata_beacon = MetadataBeacon.objects.all()
        datasets = MetadataBeaconDataset.objects.filter(
            metadata_beacon=metadata_beacon[0]
        )
        datasets_dict_list = []
        for d in datasets:
            # create json response scheme for dataset
            datasets_dict = DatasetResponse(
                d.beacon_data_id,
                d.name,
                d.assembly_id,
                d.create_date_time,
                d.update_date_time,
            ).create_dict()
            datasets_dict_list.append(datasets_dict)
        organisations = MetadataBeaconOrganization.objects.filter(
            metadata_beacon=metadata_beacon[0]
        )
        # create json response scheme for organization
        dict_org = OrganizationResponse(
            organisations[0].beacon_org_id,
            organisations[0].name,
            organisations[0].contact_url,
        ).create_dict()
        # create json output scheme for info endpoint
        output = JsonResponse(
            InfoResponse(
                metadata_beacon[0].beacon_id,
                metadata_beacon[0].name,
                metadata_beacon[0].api_version,
                datasets_dict_list,
                dict_org,
            ).create_dict(),
            json_dumps_params={"indent": 2},
        )
        # log request
        LogEntry(
            ip_address=request.META.get("REMOTE_ADDR"),
            user_identifier=request.META.get("USER"),
            remote_site=RemoteSite.objects.get(name="public"),
            date_time=timezone.now(),
            method=request.method,
            endpoint="info",
            server_protocol=request.META["SERVER_PROTOCOL"],
            status_code=output.status_code,
            response_size=len(output.content),
        ).save()
        return output


class CaseQueryEndpoint(View):
    def get(self, request, *args, **kwargs):
        """
        GET method for beacon '/query' endpoint.

        :param request: A django HttpRequest object containing query string and headers.
        :rtype: JSONResponse
        """
        chromosome = request.GET.get("referenceName")
        start = request.GET.get("start")
        end = request.GET.get("end")
        reference = request.GET.get("referenceBases")
        alternative = request.GET.get("alternateBases")
        release = request.GET.get("assemblyId")
        return self._handle(
            request, chromosome, start, end, reference, alternative, release
        )

    def post(self, request, *args, **kwargs):
        """
        POST method for beacon '/query' endpoint.

        :param request: A django HttpRequest object containing posted data and headers.
        :rtype: JSONResponse
        """
        chromosome = request.POST.get("referenceName")
        start = request.POST.get("start")
        end = request.POST.get("end")
        reference = request.POST.get("referenceBases")
        alternative = request.POST.get("alternateBases")
        release = request.POST.get("assemblyId")
        return self._handle(
            request, chromosome, start, end, reference, alternative, release
        )

    def _handle(self, request, chromosome, start, end, reference, alternative, release):
        """
        Handles request for beacon 'query' endpoint.

        :param request: A django HttpRequest object.
        :param chromosome: A string of the reference name passed by the request.
        :param start: A string of the start position passed by the request.
        :param end: A string of the end position passed by the request.
        :param reference: A string of the reference base passed by the request.
        :param alternative: A string of the alternate base passed by the request.
        :param release: A string of the release passed by the request.
        :return: JSONResponse
        """
        try:
            # set requested cases to None
            cases = [None]
            # 'collect' request parameters
            if release is None:
                release = "GRCh37"
            allele_request = AlleleRequest(
                chromosome, start, end, reference, alternative, release
            ).create_dict()
            # get metadata
            beacon_id, api_version = self._query_metadata()
            output_json = QueryResponse(
                beacon_id, api_version, allele_request
            ).create_dict()
            # authentication with password
            if "Authorization" in request.headers:
                key = request.headers["Authorization"]
            else:
                key = "public"
            remote_site = self._authenticate(key)
            # authentication failed
            if not list(remote_site):
                output_json["error"] = Error(
                    401, "You are not authorized as a user."
                ).create_dict()
                remote_site = [None]
                raise UnboundLocalError()
            # check if input parameters are valid
            if self._check_query_input(chromosome, start, end, reference, alternative):
                output_json["error"] = Error(
                    400, "The input format is invalid."
                ).create_dict()
                raise UnboundLocalError()
            # check if access limit of remote site is exceeded
            if self._check_access_limit(remote_site[0]):
                output_json["error"] = Error(
                    403, "You have exceeded your access limit."
                ).create_dict()
                raise UnboundLocalError()
            # query database for variant request
            query_parameters, cases = self._query_variant(
                remote_site[0].consortia,
                chromosome,
                start,
                end,
                reference,
                alternative,
                release,
            )
            # define json output for query endpoint
            if query_parameters.exists is False:
                output_json["exists"] = False
            else:
                output_json["exists"] = True
                output_json["datasetAlleleResponses"] = [query_parameters.create_dict()]
            output = JsonResponse(output_json, json_dumps_params={"indent": 2})
        except UnboundLocalError:  # Not authenticated or invalid arguments
            output = JsonResponse(
                output_json,
                status=output_json["error"]["errorCode"],
                json_dumps_params={"indent": 2},
            )
        # log request
        log_entry = LogEntry(
            ip_address=request.META.get("REMOTE_ADDR"),
            user_identifier=request.META.get("HTTP_X_REMOTE_USER"),
            remote_site=remote_site[0],
            date_time=timezone.now(),
            method=request.method,
            endpoint="query",
            server_protocol=request.META["SERVER_PROTOCOL"],
            release=release,
            chromosome=chromosome,
            start=start,
            end=end,
            reference=reference,
            alternative=alternative,
            status_code=output.status_code,
            response_size=len(output.content),
        )
        log_entry.save()
        log_entry.cases.set(cases)
        return output

    def _check_query_input(self, chromosome, start, end, reference, alternative):
        """
        Checks if the parameters passed by the request have a invalid format.

        :param chromosome: A string of the reference name.
        :param start: A string of the start position.
        :param end: A string of the end position.
        :param reference: A string of the reference base.
        :param alternative: A string of the alternate base.
        :return: bool: True if invalid, False otherwise
        """
        chromosome_pattern = re.compile(r"[1-9]|[1][0-9]|[2][0-2]|[XY]")
        start_pattern = re.compile(r"(\d+)")
        end_pattern = re.compile(r"(\d+)")
        reference_pattern = re.compile(r"[ACGT]+")
        alternative_pattern = re.compile(r"[ACGT]+")
        try:
            if re.fullmatch(chromosome_pattern, chromosome) is None:
                return True
            if re.fullmatch(start_pattern, start) is None:
                return True
            if re.fullmatch(end_pattern, end) is None:
                return True
            if re.fullmatch(reference_pattern, reference) is None:
                return True
            if re.fullmatch(alternative_pattern, alternative) is None:
                return True
            if int(start) > int(end):
                return True
        except TypeError:
            return True
        return False

    def _authenticate(self, key):
        """
        Authenticates the client by finding fitting remote site for key.

        :param key: A key string.
        :rtype: django QuerySet containing a RemoteSite object.
        """
        remote_site = RemoteSite.objects.filter(key=key)
        return remote_site

    def _check_access_limit(self, remote_site):
        """
        Checks if the client exceeded his access limit defined by the Remote Site.

        :param remote_site: A RemoteSite object.
        :return: bool: True if exceeded, False otherwise
        """
        access_limit = remote_site.access_limit
        if (
            LogEntry.objects.filter(
                remote_site=remote_site, date_time__contains=date.today()
            ).count()
            >= access_limit
        ):
            return True
        else:
            return False

    def _query_variant(
        self, consortia, chromosome, start, end, reference, alternative, release
    ):
        """
        Queries the database for the given variant defined by the input parameters. Returns a
        BeaconAlleleResponseObject from the json_structures module.

        :param consortia: A QuerySet of consortium objects which defining  the visibility level of the variant data.
        :param chromosome: A string of the reference name.
        :param start: A string of the start position.
        :param end: A string of the end position.
        :param reference: A string of the reference base.
        :param alternative: A string of the alternate base.
        :param release: A string of the release.
        :return: AlleleResponseObject
        """
        variant_query = CaseQueryVariant()
        # convert 0-based variant position to 1-based
        start_1_based = int(start) + 1
        # query database for requested variant
        variants = Variant.objects.filter(
            chromosome=chromosome,
            start=start_1_based,
            release=release,
            end=end,
            reference=reference,
            alternative=alternative,
            case__project__consortium__in=consortia.all(),
        ).distinct()
        cases = []
        # for each variant get summary data according to visibility level
        for v in variants:
            variant_query.exists = True
            visibility_level = self._get_highest_vis_level(v.case.project, consortia)
            if visibility_level == 25:
                variant_query.make_query_25(v)
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
            cases.append(v.case)
        # calculate frequency
        if variant_query.exists is True:
            variant_query.frequency = (
                variant_query.variant_count / variant_query.frequency_count
            )
        return (
            AlleleResponse(
                variant_query.exists,
                variant_query.sample_count,
                variant_query.variant_count_greater_ten,
                variant_query.variant_count,
                round(variant_query.frequency, 2),
                variant_query.coarse_phenotypes,
                variant_query.phenotypes,
                variant_query.case_indices,
            ),
            cases,
        )

    def _query_metadata(self):
        """
        Queries the database for the beacon metadata.

        :return: beacon_id string, api_version string
        """
        metadata_beacon = MetadataBeacon.objects.all()
        return metadata_beacon[0].beacon_id, metadata_beacon[0].api_version

    def _get_highest_vis_level(self, projects, consortia):
        """
        Looks up which is the highest visibility level for which the data from the project can be queried.

        :param projects: A project object.
        :param consortia: A consortia QuerySet.
        :return: A visibility level integer
        """
        project_consortia = Consortium.objects.filter(
            projects=projects, id__in=consortia.all().values("id")
        ).values("visibility_level")
        return min([c["visibility_level"] for c in project_consortia])
