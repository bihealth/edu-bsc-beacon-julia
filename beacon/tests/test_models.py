from django.test import TestCase
import django
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
    Consortium,
)

from .factories import (
    VariantFactory,
    PhenotypeFactory,
    CaseFactory,
    ProjectFactory,
    LogEntryFactory,
    MetadataBeaconFactory,
    MetadataBeaconOrganizationFactory,
    MetadataBeaconDatasetFactory,
    RemoteSiteFactory,
    ConsortiumFactory,
)


class TestProject(TestCase):
    """Basic test case for project model"""

    def test_create(self):
        self.assertEqual(Project.objects.count(), 0)
        ProjectFactory()
        self.assertEqual(Project.objects.count(), 1)


class TestCase(TestCase):
    """Basic test case for case model"""

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        CaseFactory()
        self.assertEqual(Case.objects.count(), 1)


class TestLogEntry(TestCase):
    """Basic test case for logEntry model"""

    def test_create(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        LogEntryFactory()
        self.assertEqual(LogEntry.objects.count(), 1)


class TestVariant(TestCase):
    """Basic test case for variant model"""

    #: Set ups for different cases allele counts
    def setUp(self):
        self.variant_autosome = VariantFactory(chromosome=1)
        self.variant_allosome_X = VariantFactory(chromosome=23)
        self.variant_allosome_Y = VariantFactory(chromosome=24)

    def test_create(self):
        self.assertEqual(Variant.objects.count(), 3)
        VariantFactory()
        self.assertEqual(Variant.objects.count(), 4)

    #: Test method _get_variant_sample_count for autosome
    def test_get_variant_sample_count_autosome(self):
        (
            variant_count,
            sample_count,
            frequency_count,
        ) = self.variant_autosome.get_variant_sample_frequency_count()
        self.assertEqual(variant_count, 1)
        self.assertEqual(sample_count, 1)
        self.assertEqual(frequency_count, 2)

    #: Test method _get_variant_sample_count for allosome
    def test_get_variant_sample_count_allosome(self):
        (
            variant_count,
            sample_count,
            frequency_count,
        ) = self.variant_allosome_X.get_variant_sample_frequency_count()
        self.assertEqual(frequency_count, 1)
        (
            variant_count,
            sample_count,
            frequency_count,
        ) = self.variant_allosome_Y.get_variant_sample_frequency_count()
        self.assertEqual(frequency_count, 1)


class TestPhenotype(TestCase):
    """Basic test case for phenotype model"""

    #: Set up phenotype
    def setUp(self):
        self.phenotype = PhenotypeFactory(phenotype="HP:0012211")

    def test_create(self):
        self.assertEqual(Phenotype.objects.count(), 1)
        PhenotypeFactory()
        self.assertEqual(Phenotype.objects.count(), 2)

    #: Test method _get_coarse_phenotype
    def test_get_coarse_phenotype(self):
        coarse_phenotype = self.phenotype.get_coarse_phenotype()
        self.assertIsInstance(coarse_phenotype, set)
        self.assertIn("HP:0010935", coarse_phenotype)
        coarse_phenotype_already_coarse = PhenotypeFactory(
            phenotype="HP:0000118"
        ).get_coarse_phenotype()
        self.assertEqual(coarse_phenotype_already_coarse, {"HP:0000118"})


class TestConsortium(TestCase):
    """Basic test case for consortium model"""

    def test_create(self):
        self.assertEqual(Consortium.objects.count(), 0)
        ConsortiumFactory()
        self.assertEqual(Consortium.objects.count(), 1)


class TestRemoteSite(TestCase):
    """Basic test case for remote site model"""

    def test_create(self):
        self.assertEqual(RemoteSite.objects.count(), 0)
        RemoteSiteFactory()
        self.assertEqual(RemoteSite.objects.count(), 1)

    #: Test unique constraint remote site key
    def test_key_unique(self):
        RemoteSiteFactory(key="x")
        self.assertRaises(django.db.utils.IntegrityError, RemoteSiteFactory, key="x")


class TestCaseLogEntry(TestCase):
    """Basic test case for logEntry model"""

    def testCreate(self):
        self.assertEqual(LogEntry.objects.count(), 0)
        LogEntryFactory()
        self.assertEqual(LogEntry.objects.count(), 1)


class TestMetadataBeacon(TestCase):
    """Basic test case for metadata beacon model"""

    def test_create(self):
        self.assertEqual(MetadataBeacon.objects.count(), 0)
        MetadataBeaconFactory()
        self.assertEqual(MetadataBeacon.objects.count(), 1)


class TestMetadataBeaconOrganization(TestCase):
    """Basic test case for metadata beacon organization model"""

    def test_create(self):
        self.assertEqual(MetadataBeaconOrganization.objects.count(), 0)
        MetadataBeaconOrganizationFactory()
        self.assertEqual(MetadataBeaconOrganization.objects.count(), 1)


class TestMetadataBeaconDataset(TestCase):
    """Basic test case for metadata beacon dataset model"""

    def test_create(self):
        self.assertEqual(MetadataBeaconDataset.objects.count(), 0)
        MetadataBeaconDatasetFactory()
        self.assertEqual(MetadataBeaconDataset.objects.count(), 1)
