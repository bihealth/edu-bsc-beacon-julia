from django.test import TestCase
import django
import factory
from ..models import (
        Variant,
        Phenotype,
        Case,
        Project,
        LogEntry,
        MetadataBeacon,
        MetadataBeaconOrganization,
        MetadataBeaconDataset,
        RemoteSite,
        Consortium
    )

from .factories import (
        VariantFactory,
        PhenotypeFactory,
        CaseFactory,
        ProjectFactory,
       # LogEntryFactory,
        MetadataBeaconFactory,
        MetadataBeaconOrganizationFactory,
        MetadataBeaconDatasetFactory,
        RemoteSiteFactory,
        ConsortiumFactory
    )


class TestProject(TestCase):
    def test_create(self):
        self.assertEqual(Project.objects.count(), 0)
        ProjectFactory()
        self.assertEqual(Project.objects.count(), 1)


class TestCase(TestCase):
    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        CaseFactory()
        self.assertEqual(Case.objects.count(), 1)


class TestVariant(TestCase):
    def setUp(self):
        self.variant = VariantFactory()

    def test_create(self):
        self.assertEqual(Variant.objects.count(), 1)
        VariantFactory()
        self.assertEqual(Variant.objects.count(), 2)

    def test_get_allele_count(self):
        allele_count = self.variant.get_allele_count()
        self.assertIsInstance(allele_count, int)
        self.assertEqual(allele_count, 1)


class TestPhenotype(TestCase):
    def setUp(self):
        self.phenotype = PhenotypeFactory(phenotype="HP:0012211")

    def test_create(self):
        self.assertEqual(Phenotype.objects.count(), 1)
        PhenotypeFactory()
        self.assertEqual(Phenotype.objects.count(), 2)

    def test_get_coarse_phenotype(self):
        coarse_phenotype = self.phenotype.get_coarse_phenotype()
        self.assertIsInstance(coarse_phenotype, list)
        self.assertIn("HP:0011277", coarse_phenotype)
        coarse_phenotype_already_coarse = PhenotypeFactory(phenotype="HP:0000001").get_coarse_phenotype()
        self.assertEqual(coarse_phenotype_already_coarse, "HP:0000001")


class TestConsortium(TestCase):
    def test_create(self):
        self.assertEqual(Consortium.objects.count(), 0)
        ConsortiumFactory()
        self.assertEqual(Consortium.objects.count(), 1)


class TestRemoteSite(TestCase):
    def test_create(self):
        self.assertEqual(RemoteSite.objects.count(), 0)
        RemoteSiteFactory()
        self.assertEqual(RemoteSite.objects.count(), 1)

    def test_key_unique(self):
        RemoteSiteFactory(key="x")
        self.assertRaises(django.db.utils.IntegrityError, RemoteSiteFactory, key='x')

#TODO: test logentry
#class TestCaseLogEntry(TestCase):
    #def setUp(self):

 #   def testCreate(self):
   #     self.assertEqual(LogEntry.objects.count(), 0)
  #      LogEntryFactory()
    #    self.assertEqual(LogEntry.objects.count(), 1


class TestMetadataBeacon(TestCase):
    def test_create(self):
        self.assertEqual(MetadataBeacon.objects.count(), 0)
        MetadataBeaconFactory()
        self.assertEqual(MetadataBeacon.objects.count(), 1)


class TestMetadataBeaconOrganization(TestCase):
    def test_create(self):
        self.assertEqual(MetadataBeaconOrganization.objects.count(), 0)
        MetadataBeaconOrganizationFactory()
        self.assertEqual(MetadataBeaconOrganization.objects.count(), 1)


class TestMetadataBeaconDataset(TestCase):
    def test_create(self):
        self.assertEqual(MetadataBeaconDataset.objects.count(), 0)
        MetadataBeaconDatasetFactory()
        self.assertEqual(MetadataBeaconDataset.objects.count(), 1)