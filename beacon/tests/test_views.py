import datetime

from django.test import TestCase
from django.urls import reverse
#from unittest import TestCase
from .factories import (
    MetadataBeaconFactory,
    MetadataBeaconOrganizationFactory,
    MetadataBeaconDatasetFactory,
    RemoteSiteFactory
)
from ..views import CaseInfoEndpoint, CaseQueryEndpoint
from ..models import LogEntry, MetadataBeaconDataset, RemoteSite
from django.http import JsonResponse
from django.test import Client


class TestCaseInfoEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        ## TODO: MetadataEndpointFactory()
        self.metadata_beacon = MetadataBeaconFactory()
        self.metadata_organization = MetadataBeaconOrganizationFactory(metadata_beacon=self.metadata_beacon)
        self.metadata_dataset = MetadataBeaconDatasetFactory(metadata_beacon=self.metadata_beacon)
        self.remote_site = RemoteSiteFactory(name='public')

    def test_get_info(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(reverse('info'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            JsonResponse({
                "id": str(self.metadata_beacon.beacon_id),
                "name": self.metadata_beacon.name,
                "apiVersion": self.metadata_beacon.api_version,
                "datasets": [
                    {
                        "id": str(self.metadata_dataset.beacon_data_id),
                        "name": self.metadata_dataset.name,
                        "assemblyId": self.metadata_dataset.assembly_id,
                        "createDateTime": str(self.metadata_dataset.create_date_time),
                        "updateDateTime": str(self.metadata_dataset.update_date_time),
                    }
                ],
                "organization": {
                    "id": str(self.metadata_organization.beacon_org_id),
                    "name": self.metadata_organization.name,
                    "contactUrl": self.metadata_organization.contact_url,
                },

            }, json_dumps_params={'indent': 2}
            ).content)
        self.assertEqual(LogEntry.objects.count(), 1)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, self.remote_site)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertIn('GET', log.request)
        self.assertEqual(log.status_code, 200)
        self.assertIsInstance(log.response_size, int)


class TestCaseQueryEndpoint(TestCase):
    def setUp(self):
        self.client = Client()
        self.metadata_beacon = MetadataBeaconFactory()
        self.metadata_organization = MetadataBeaconOrganizationFactory(metadata_beacon=self.metadata_beacon)
        self.metadata_dataset = MetadataBeaconDatasetFactory(metadata_beacon=self.metadata_beacon)
        self.remote_site_public = RemoteSiteFactory(name='public', key='public')
        self.remote_site_xxx = RemoteSiteFactory(key='xxx')

    def test_get_query_no_input(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(reverse('query'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, JsonResponse({
            "beaconId": str(self.metadata_beacon.beacon_id),
            "apiVersion": self.metadata_beacon.api_version,
            "exists": None,
            "error": {
                "errorCode": 400,
                "errorMessage": "The input format is invalid."

            },
            "alleleRequest": {"referenceName": None,
                              "start": None,
                              "end": None,
                              "referenceBases": None,
                              "alternateBases": None,
                              "assemblyId": "GRCh37"
                              },
            "datasetAlleleResponses": [],
        }, json_dumps_params={'indent': 2}
        ).content)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, None)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertIn('GET', log.request)
        self.assertEqual(log.status_code, 400)
        self.assertIsInstance(log.response_size, int)

    def test_get_query_invalid_input(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(reverse("query"), {"reerenceName": 1,
                                                      "start": 12345,
                                                      "end": 12345,
                                                      "referenceBases": "C",
                                                      "alternateBases": "T"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, JsonResponse({
            "beaconId": str(self.metadata_beacon.beacon_id),
            "apiVersion": self.metadata_beacon.api_version,
            "exists": None,
            "error": {
                "errorCode": 400,
                "errorMessage": "The input format is invalid."

            },
            "alleleRequest": {"referenceName": None,
                              "start": "12345",
                              "end": "12345",
                              "referenceBases": "C",
                              "alternateBases": "T",
                              "assemblyId": "GRCh37"
                              },
            "datasetAlleleResponses": [],
        }, json_dumps_params={'indent': 2}
        ).content)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, None)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertIn('GET', log.request)
        self.assertEqual(log.status_code, 400)
        self.assertIsInstance(log.response_size, int)

    def test_get_query_with_assemblyId(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        response = self.client.get(reverse("query"), {"referenceName": 1,
                                                      "start": 12345,
                                                      "end": 12345,
                                                      "referenceBases": "C",
                                                      "alternateBases": "T",
                                                      "assemblyId": "GRCh38"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, JsonResponse({
            "beaconId": str(self.metadata_beacon.beacon_id),
            "apiVersion": self.metadata_beacon.api_version,
            "exists": False,
            "error": None,
            "alleleRequest": {"referenceName": "1",
                              "start": "12345",
                              "end": "12345",
                              "referenceBases": "C",
                              "alternateBases": "T",
                              "assemblyId": "GRCh38"
                              },
            "datasetAlleleResponses": [],
        }, json_dumps_params={'indent': 2}
        ).content)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertIn('GET', log.request)
        self.assertEqual(log.status_code, 200)
        self.assertIsInstance(log.response_size, int)

    def test_get_query_authorization_with_key(self):
        response = self.client.get(reverse("query"), {
            "referenceName": 1,
            "start": 12345,
            "end": 12345,
            "referenceBases": "C",
            "alternateBases": "T"}, AUTHORIZATION='xxx')
        # self.assertEqual("Authorization", self.client.headers)
        self.assertEqual(response.status_code, 200)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser.key, "xxx")

    def test_post_query(self):
        response = self.client.post(reverse("query"), {"referenceName": 1,
                                                       "start": 12345,
                                                       "end": 12345,
                                                       "referenceBases": "C",
                                                       "alternateBases": "T"}
                                    )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, JsonResponse({
            "beaconId": str(self.metadata_beacon.beacon_id),
            "apiVersion": self.metadata_beacon.api_version,
            "exists": False,
            "error": None,
            "alleleRequest": {"referenceName": "1",
                              "start": "12345",
                              "end": "12345",
                              "referenceBases": "C",
                              "alternateBases": "T",
                              "assemblyId": "GRCh37"
                              },
            "datasetAlleleResponses": [],
        }, json_dumps_params={'indent': 2}
        ).content)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_identifier, None)
        self.assertEqual(log.authuser, self.remote_site_public)
        self.assertIsInstance(log.date_time, datetime.datetime)
        self.assertIn('POST', log.request)
        self.assertEqual(log.status_code, 200)
        self.assertIsInstance(log.response_size, int)

    def test_get_query_authorization_without_key(self):
        response = self.client.get(reverse("query"), {"Authorization": "",
                                                      "referenceName": 1,
                                                      "start": 12345,
                                                      "end": 12345,
                                                      "referenceBases": "C",
                                                      "alternateBases": "T"}
                                   )
        self.assertEqual(response.status_code, 200)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, self.remote_site_public)
        response = self.client.get(reverse("query"), {"referenceName": 1,
                                                      "start": 12345,
                                                      "end": 12345,
                                                      "referenceBases": "C",
                                                      "alternateBases": "T"}
                                   )
        self.assertEqual(response.status_code, 200)
        log = LogEntry.objects.all()[1]
        self.assertEqual(log.authuser, self.remote_site_public)

    def test_get_query_authorization_invalid_key(self):
        response = self.client.get(reverse("query"), {"Authorization": "xy",
                                                      "referenceName": 1,
                                                      "start": 12345,
                                                      "end": 12345,
                                                      "referenceBases": "C",
                                                      "alternateBases": "T"}
                                   )
        self.assertEqual(response.content, JsonResponse({
            "beaconId": str(self.metadata_beacon.beacon_id),
            "apiVersion": self.metadata_beacon.api_version,
            "exists": None,
            "error": {
                "errorCode": 401,
                "errorMessage": "You are not authorized as a user."

            },
            "alleleRequest": {"referenceName": "1",
                              "start": "12345",
                              "end": "12345",
                              "referenceBases": "C",
                              "alternateBases": "T",
                              "assemblyId": "GRCh37"
                              },
            "datasetAlleleResponses": [],
        }, json_dumps_params={'indent': 2}
        ).content)
        self.assertEqual(response.status_code, 401)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, None)
        self.assertEqual(log.status_code, 401)

    def test_get_query_exceeded_access_limit(self):
        remote_site_zero_access = RemoteSiteFactory(key="0_access", access_limit=0)
        response = self.client.get(reverse("query"), {"Authorization": "0_access",
                                                      "referenceName": 1,
                                                      "start": 12345,
                                                      "end": 12345,
                                                      "referenceBases": "C",
                                                      "alternateBases": "T"}
                                   )
        self.assertEqual(response.content, JsonResponse({
            "beaconId": str(self.metadata_beacon.beacon_id),
            "apiVersion": self.metadata_beacon.api_version,
            "exists": None,
            "error": {
                "errorCode": 403,
                "errorMessage": "You have exceeded your access limit."

            },
            "alleleRequest": {"referenceName": "1",
                              "start": "12345",
                              "end": "12345",
                              "referenceBases": "C",
                              "alternateBases": "T",
                              "assemblyId": "GRCh37"
                              },
            "datasetAlleleResponses": [],
        }, json_dumps_params={'indent': 2}
        ).content)
        self.assertEqual(response.status_code, 403)
        log = LogEntry.objects.all()[0]
        self.assertEqual(log.authuser, remote_site_zero_access)
        self.assertEqual(log.status_code, 403)

    def test_query_check_query_input(self):
        c = CaseQueryEndpoint()
        chromosome = "X"
        start = "12345"
        end = "12346"
        reference = "CC"
        alternative = "T"
        self.assertEqual(c._check_query_input(chromosome, start, end, reference, alternative), False)
        for i in enumerate(list(range(1, 23)) + ["X", "Y"]):
            self.assertEqual(c._check_query_input(i, start, end, reference, alternative), True)
        self.assertEqual(c._check_query_input(chromosome, "x", end, reference, alternative), True)
        self.assertEqual(c._check_query_input(chromosome, start, "x", reference, alternative), True)
        self.assertEqual(c._check_query_input(chromosome, start, end, "H", alternative), True)
        self.assertEqual(c._check_query_input(chromosome, start, end, reference, "H"), True)
        self.assertEqual(c._check_query_input(chromosome, start, "1234", reference, "H"), True)
