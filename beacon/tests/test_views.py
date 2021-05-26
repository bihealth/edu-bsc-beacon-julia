import datetime
from django.test import TestCase
from django.urls import reverse
from .factories import (
    MetadataBeaconFactory,
    MetadataBeaconOrganizationFactory,
    MetadataBeaconDatasetFactory,
    RemoteSiteFactory,
    VariantFactory,
    ConsortiumFactory,
    CaseFactory,
    ProjectFactory,
    PhenotypeFactory,
)
from ..views import CaseQueryEndpoint
from ..models import (
    LogEntry,
    RemoteSite,
    Variant,
    Project,
    Phenotype,
    Case,
    Consortium,
)
from django.http import JsonResponse
from django.test import Client


class TestCaseInfoEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        # TODO: MetadataEndpointFactory()
        self.metadata_beacon = MetadataBeaconFactory()
        self.metadata_organization = MetadataBeaconOrganizationFactory(
            metadata_beacon=self.metadata_beacon
        )
        self.metadata_dataset = MetadataBeaconDatasetFactory(
            metadata_beacon=self.metadata_beacon
        )
        self.remote_site = RemoteSiteFactory(name="public")

    def test_get_info(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(reverse("info"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "id": str(self.metadata_beacon.beacon_id),
                    "name": self.metadata_beacon.name,
                    "apiVersion": self.metadata_beacon.api_version,
                    "datasets": [
                        {
                            "id": str(self.metadata_dataset.beacon_data_id),
                            "name": self.metadata_dataset.name,
                            "assemblyId": self.metadata_dataset.assembly_id,
                            "createDateTime": str(
                                self.metadata_dataset.create_date_time
                            ),
                            "updateDateTime": str(
                                self.metadata_dataset.update_date_time
                            ),
                        }
                    ],
                    "organization": {
                        "id": str(self.metadata_organization.beacon_org_id),
                        "name": self.metadata_organization.name,
                        "contactUrl": self.metadata_organization.contact_url,
                    },
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, self.remote_site)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertEqual("GET;/;HTTP/1.1", log.request)
        self.assertEqual(log.status_code, 200)
        self.assertIsInstance(log.response_size, int)


class TestCaseQueryEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.metadata_beacon = MetadataBeaconFactory()
        self.metadata_organization = MetadataBeaconOrganizationFactory(
            metadata_beacon=self.metadata_beacon
        )
        self.metadata_dataset = MetadataBeaconDatasetFactory(
            metadata_beacon=self.metadata_beacon
        )
        self.remote_site_public = RemoteSiteFactory(name="public", key="public")
        self.remote_site_xxx = RemoteSiteFactory(key="xxx")

    def test_get_query(self):
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": False,
                    "error": None,
                    "alleleRequest": {
                        "referenceName": "1",
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertEqual(
            "GET;"
            "/query;"
            "[('referenceName', '1'),"
            " ('start', '12344'),"
            " ('end', '12345'),"
            " ('referenceBases', 'C'),"
            " ('alternateBases', 'T')];"
            "HTTP/1.1",
            log.request,
        )
        self.assertEqual(log.status_code, 200)
        self.assertIsInstance(log.response_size, int)

    def test_post_query(self):
        response = self.client.post(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": False,
                    "error": None,
                    "alleleRequest": {
                        "referenceName": "1",
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertEqual(
            "POST;"
            "/query;"
            "[('referenceName', '1'),"
            " ('start', '12344'),"
            " ('end', '12345'),"
            " ('referenceBases', 'C'),"
            " ('alternateBases', 'T')];"
            "HTTP/1.1",
            log.request,
        )
        self.assertEqual(log.status_code, 200)
        self.assertIsInstance(log.response_size, int)

    def test_get_query_no_input(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(reverse("query"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": None,
                    "error": {
                        "errorCode": 400,
                        "errorMessage": "The input format is invalid.",
                    },
                    "alleleRequest": {
                        "referenceName": None,
                        "start": None,
                        "end": None,
                        "referenceBases": None,
                        "alternateBases": None,
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertEqual("GET;/query;[];HTTP/1.1", log.request)
        self.assertEqual(log.status_code, 400)

    def test_get_query_invalid_input(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(
            reverse("query"),
            {
                "reerenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": None,
                    "error": {
                        "errorCode": 400,
                        "errorMessage": "The input format is invalid.",
                    },
                    "alleleRequest": {
                        "referenceName": None,
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertEqual(
            "GET;"
            "/query;"
            "[('reerenceName', '1'),"
            " ('start', '12344'),"
            " ('end', '12345'),"
            " ('referenceBases', 'C'),"
            " ('alternateBases', 'T')];"
            "HTTP/1.1",
            log.request,
        )
        self.assertEqual(log.status_code, 400)

    def test_get_query_with_assemblyId(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
                "assemblyId": "GRCh38",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": False,
                    "error": None,
                    "alleleRequest": {
                        "referenceName": "1",
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh38",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertEqual(
            "GET;"
            "/query;"
            "[('referenceName', '1'),"
            " ('start', '12344'),"
            " ('end', '12345'),"
            " ('referenceBases', 'C'),"
            " ('alternateBases', 'T'),"
            " ('assemblyId', 'GRCh38')];"
            "HTTP/1.1",
            log.request,
        )
        self.assertEqual(log.status_code, 200)

    def test_get_query_authorization_with_key_and_user_identifier(self):
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
            HTTP_AUTHORIZATION="xxx",
            HTTP_X_REMOTE_USER="user",
        )
        self.assertEqual(response.status_code, 200)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser.key, "xxx")
        self.assertEqual(log.user_identifier, "user")

    def test_get_query_authorization_without_key_and_user_identifier(self):
        response = self.client.get(
            reverse("query"),
            {
                "Authorization": "",
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
        )
        self.assertEqual(response.status_code, 200)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, self.remote_site_public)
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
        )
        self.assertEqual(response.status_code, 200)
        log = LogEntry.objects.all()[1]
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertEqual(log.user_identifier, None)

    def test_get_query_authorization_invalid_key(self):
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
            HTTP_AUTHORIZATION="xy",
        )
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": None,
                    "error": {
                        "errorCode": 401,
                        "errorMessage": "You are not authorized as a user.",
                    },
                    "alleleRequest": {
                        "referenceName": "1",
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        self.assertEqual(response.status_code, 401)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, None)
        self.assertEqual(log.status_code, 401)

    def test_get_query_exceeded_access_limit(self):
        remote_site_zero_access = RemoteSiteFactory(key="0_access", access_limit=0)
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
            HTTP_AUTHORIZATION="0_access",
        )
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": None,
                    "error": {
                        "errorCode": 403,
                        "errorMessage": "You have exceeded your access limit.",
                    },
                    "alleleRequest": {
                        "referenceName": "1",
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        self.assertEqual(response.status_code, 403)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, remote_site_zero_access)
        self.assertEqual(log.status_code, 403)

    def test_get_query_no_project_permission(self):
        p = ProjectFactory()
        con = ConsortiumFactory(projects=None)
        c = CaseFactory(project=p)
        VariantFactory(case=c)
        PhenotypeFactory(case=c)
        RemoteSiteFactory(key="x", consortia=[con])
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Consortium.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(Variant.objects.count(), 1)
        self.assertEqual(Phenotype.objects.count(), 1)
        self.assertEqual(RemoteSite.objects.count(), 3)
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
            HTTP_AUTHORIZATION="x",
        )
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": False,
                    "error": None,
                    "alleleRequest": {
                        "referenceName": "1",
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LogEntry.objects.count(), 1)

    def test_get_query_mixed_vis_level(self):
        p1 = ProjectFactory()
        p2 = ProjectFactory()
        p3 = ProjectFactory()
        p4 = ProjectFactory()
        p5 = ProjectFactory()
        p6 = ProjectFactory()
        con1 = ConsortiumFactory(projects=[p1], visibility_level=0)
        con2 = ConsortiumFactory(projects=[p3], visibility_level=5)
        con3 = ConsortiumFactory(projects=[p2], visibility_level=20)
        con4 = ConsortiumFactory(projects=[p1, p2], visibility_level=15)
        con5 = ConsortiumFactory(projects=[p4], visibility_level=10)
        con6 = ConsortiumFactory(projects=[p5], visibility_level=20)
        con7 = ConsortiumFactory(projects=[p6], visibility_level=25)
        c1 = CaseFactory(project=p1)
        c2 = CaseFactory(project=p1)
        c3 = CaseFactory(project=p2, structure="quartet", inheritance="dominant")
        c4 = CaseFactory(project=p2, structure="quartet", inheritance="dominant")
        c5 = CaseFactory(project=p3, structure="quartet", inheritance="dominant")
        c6 = CaseFactory(project=p6, structure="quartet", inheritance="dominant")
        v1 = VariantFactory(
            case=c1,
            chromosome=1,
            start=12345,
            end=12345,
            reference="C",
            alternative="T",
        )
        v2 = VariantFactory(
            case=c2,
            chromosome=1,
            start=12345,
            end=12345,
            reference="C",
            alternative="T",
        )
        VariantFactory(
            case=c3,
            chromosome=1,
            start=12345,
            end=12345,
            reference="C",
            alternative="T",
        )
        VariantFactory(
            case=c4,
            chromosome=1,
            start=12345,
            end=12345,
            reference="C",
            alternative="T",
        )
        VariantFactory(
            case=c5,
            chromosome=1,
            start=12345,
            end=12345,
            reference="C",
            alternative="T",
        )
        VariantFactory(
            case=c6,
            chromosome=1,
            start=12345,
            end=12345,
            reference="C",
            alternative="T",
        )
        PhenotypeFactory(case=c1)
        PhenotypeFactory(case=c2)
        PhenotypeFactory(case=c3)
        PhenotypeFactory(case=c4)
        PhenotypeFactory(case=c5)
        RemoteSiteFactory(key="x", consortia=[con1, con2, con3, con4, con5, con6, con7])
        self.assertEqual(Project.objects.count(), 6)
        self.assertEqual(Consortium.objects.count(), 7)
        self.assertEqual(Case.objects.count(), 6)
        self.assertEqual(Variant.objects.count(), 6)
        self.assertEqual(Phenotype.objects.count(), 5)
        self.assertEqual(RemoteSite.objects.count(), 3)
        response = self.client.get(
            reverse("query"),
            {
                "referenceName": 1,
                "start": 12344,
                "end": 12345,
                "referenceBases": "C",
                "alternateBases": "T",
            },
            HTTP_AUTHORIZATION="x",
        )
        self.assertEqual(
            response.content,
            JsonResponse(
                {
                    "beaconId": str(self.metadata_beacon.beacon_id),
                    "apiVersion": self.metadata_beacon.api_version,
                    "exists": True,
                    "error": None,
                    "alleleRequest": {
                        "referenceName": "1",
                        "start": "12344",
                        "end": "12345",
                        "referenceBases": "C",
                        "alternateBases": "T",
                        "assemblyId": "GRCh37",
                    },
                    "datasetAlleleResponses": [
                        {
                            "exists": True,
                            "sampleCount": 14,
                            "variantCount>10": True,
                            "variantCount": 11,
                            "frequency": 0.39,
                            "coarsePhenotype": [],
                            "phenotype": ["HP:0001039", "HP:0001049", "HP:0001166"],
                            "caseName": [str(v1.case.index), str(v2.case.index)],
                            "error": None,
                        },
                    ],
                },
                json_dumps_params={"indent": 2},
            ).content,
        )
        self.assertEqual(response.status_code, 200)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.cases.all()[::1], [c1, c2, c3, c4, c5, c6])

    def test_query_check_query_input(self):
        c = CaseQueryEndpoint()
        chromosome = "X"
        start = "12345"
        end = "12346"
        reference = "CC"
        alternative = "T"
        self.assertEqual(
            c._check_query_input(chromosome, start, end, reference, alternative), False
        )
        for i in enumerate(list(range(1, 23)) + ["X", "Y"]):
            self.assertEqual(
                c._check_query_input(i, start, end, reference, alternative), True
            )
        self.assertEqual(
            c._check_query_input(chromosome, "x", end, reference, alternative), True
        )
        self.assertEqual(
            c._check_query_input(chromosome, start, "x", reference, alternative), True
        )
        self.assertEqual(
            c._check_query_input(chromosome, start, end, "H", alternative), True
        )
        self.assertEqual(
            c._check_query_input(chromosome, start, end, reference, "H"), True
        )
        self.assertEqual(
            c._check_query_input(chromosome, start, "1234", reference, alternative), True
        )
