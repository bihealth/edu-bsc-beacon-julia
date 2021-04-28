import datetime

from django.test import TestCase, RequestFactory
from .factories import (
        MetadataBeaconFactory,
        MetadataBeaconOrganizationFactory,
        MetadataBeaconDatasetFactory,
        RemoteSiteFactory
    )
from ..views import CaseInfoEndpoint, CaseQueryEndpoint
from ..models import LogEntry
from django.http import JsonResponse
import json



class TestCaseInfoEndpoint(TestCase):
    def setUp(self):
        self.client = RequestFactory()
        self.metadata_beacon = MetadataBeaconFactory()
        self.metadata_organization = MetadataBeaconOrganizationFactory(metadata_beacon=self.metadata_beacon)
        self.metadata_dataset = MetadataBeaconDatasetFactory(metadata_beacon=self.metadata_beacon)
        self.remote_site = RemoteSiteFactory(name='public')

    def test_get_info(self):
        import pdb; pdb.set_trace()
        request = self.client.get('/')
        self.assertEqual(LogEntry.objects.count(), 0)
        response = CaseInfoEndpoint.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content,
            JsonResponse({
                "id": str(self.metadata_beacon.beacon_id),
                "name": self.metadata_beacon.name,
                "apiVersion": self.metadata_beacon.api_version,
                "datasets": [
                    {
                        "id": str(self.metadata_dataset.id),
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
        self.client = RequestFactory()
        self.metadata_beacon = MetadataBeaconFactory()
        self.metadata_organization = MetadataBeaconOrganizationFactory(metadata_beacon=self.metadata_beacon)
        self.metadata_dataset = MetadataBeaconDatasetFactory(metadata_beacon=self.metadata_beacon)
        self.remote_site = RemoteSiteFactory(name='public')

    def test_get_query(self):
        import pdb; pdb.set_trace()
        request = self.client.get('/query')
        self.assertEqual(LogEntry.objects.count(), 0)
        response = CaseInfoEndpoint.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content[50:], JsonResponse({
                "beaconId": str(self.metadata_beacon.beacon_id),
                "apiVersion": self.metadata_beacon.api_version,
                "alleleRequest": {"referenceName": None,
                                  "start": None,
                                  "end": None,
                                  "referenceBases": None,
                                  "alternateBases": None,
                                  "assemblyId": "GRCh37"},
                "exists": None,
                "error":
                    {
                        "errorMessage": str(self.metadata_dataset.id),
                        "errorCode": 403,
                    },
                "datasetAlleleResponses": [],

            }, json_dumps_params={'indent': 2}
            ).content[50:])

    def test_post_query(self):
        pass

