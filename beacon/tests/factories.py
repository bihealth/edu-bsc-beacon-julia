import factory
from django.utils import timezone
import random
import string
from ..models import (
    Project,
    Case,
    Variant,
    RemoteSite,
    Consortium,
    Phenotype,
    LogEntry,
    MetadataBeacon,
    MetadataBeaconOrganization,
    MetadataBeaconDataset,
)


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Project`` objects."""

    class Meta:
        model = Project

    title = factory.Sequence(lambda n: 'Project %d' % n)


class CaseFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Case`` objects."""

    class Meta:
        model = Case

    class Params:
        #: The sex of the index
        sex = 1  # 1: unaffected, 2: affected
        #: The structure can be "singleton", "trio" or "quartet" at the moment.
        structure = "singleton"
        #: The supported inheritance patterns are "denovo", "dominant", and "recessive" at the
        #: moment.  This is only used for non-singletons.  When dominant, the father will be
        #: affected.
        inheritance = "denovo"

    project = factory.SubFactory(ProjectFactory)
    name = factory.LazyAttributeSequence(lambda o, n: "case %03d: %s" % (n, o.structure))
    index = factory.Sequence(lambda n: "index_%03d-N1-DNA1-WES1" % n)
    pedigree = []

    @factory.lazy_attribute_sequence
    def pedigree(self, n):
        if self.structure not in (
                "singleton",
                "duo",
                "trio",
                "trio-noparents",
                "quartet",
                "quintet",
        ):
            raise ValueError("Invalid structure type!")
        elif self.structure == "singleton":
            return [
                {
                    "patient": self.index,
                    "father": "0",
                    "mother": "0",
                    "sex": self.sex,
                    "affected": 2,
                    "has_gt_entries": True,
                }
            ]
        elif self.structure == "duo":
            father = "father_%03d-N1-DNA1-WES1" % n
            return [
                {
                    "patient": self.index,
                    "father": father,
                    "mother": "0",
                    "sex": self.sex,
                    "affected": 2,  # always affected
                    "has_gt_entries": True,
                },
                {
                    "patient": father,
                    "father": "0",
                    "mother": "0",
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": True,
                },
            ]
        elif self.structure == "trio":
            # Father and mother name
            father = "father_%03d-N1-DNA1-WES1" % n
            mother = "mother_%03d-N1-DNA1-WES1" % n
            return [
                {
                    "patient": self.index,
                    "father": father,
                    "mother": mother,
                    "sex": self.sex,
                    "affected": 2,  # always affected
                    "has_gt_entries": True,
                },
                {
                    "patient": father,
                    "father": "0",
                    "mother": "0",
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": True,
                },
                {
                    "patient": mother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": True,
                },
            ]
        elif self.structure == "trio-noparents":
            # Father and mother name
            father = "father_%03d-N1-DNA1-WES1" % n
            mother = "mother_%03d-N1-DNA1-WES1" % n
            return [
                {
                    "patient": self.index,
                    "father": father,
                    "mother": mother,
                    "sex": self.sex,
                    "affected": 2,  # always affected
                    "has_gt_entries": True,
                },
                {
                    "patient": father,
                    "father": "0",
                    "mother": "0",
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": False,
                },
                {
                    "patient": mother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": False,
                },
            ]
        elif self.structure == "quartet":
            # Father - Mother - Siblings
            father = "father_%03d-N1-DNA1-WES1" % n
            mother = "mother_%03d-N1-DNA1-WES1" % n
            sibling = "sibling_%03d-N1-DNA1-WES1" % n
            return [
                {
                    "patient": self.index,
                    "father": father,
                    "mother": mother,
                    "sex": self.sex,
                    "affected": 2,  # always affected
                    "has_gt_entries": True,
                },
                {
                    "patient": sibling,
                    "father": father,
                    "mother": mother,
                    "sex": (self.sex % 2) + 1,  # make sibling the opposite sex
                    "affected": 2,  # always affected
                    "has_gt_entries": True,
                },
                {
                    "patient": father,
                    "father": "0",
                    "mother": "0",
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": True,
                },
                {
                    "patient": mother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": True,
                },
            ]
        else:  # self.structure == "quintet":
            # Index - Father - Mother - Grandfather - Grandmother
            father = "father_%03d-N1-DNA1-WES1" % n
            mother = "mother_%03d-N1-DNA1-WES1" % n
            grandfather = "grandfather_%03d-N1-DNA1-WES1" % n
            grandmother = "grandmother_%03d-N1-DNA1-WES1" % n
            return [
                {
                    "patient": self.index,
                    "father": father,
                    "mother": mother,
                    "sex": self.sex,
                    "affected": 2,  # always affected
                    "has_gt_entries": True,
                },
                {
                    "patient": father,
                    "father": grandfather,
                    "mother": grandmother,
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": True,
                },
                {
                    "patient": mother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": True,
                },
                {
                    "patient": grandfather,
                    "father": "0",
                    "mother": "0",
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": True,
                },
                {
                    "patient": grandmother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": True,
                },
            ]


CHROMOSOME_MAPPING = {str(chrom): i + 1 for i, chrom in enumerate(list(range(1, 23)) + ["X", "Y"])}


class VariantFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Variant`` objects."""

    class Meta:
        model = Variant

    release = "GRCh37"
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    case = factory.SubFactory(CaseFactory)

    @factory.lazy_attribute
    def genotype(self):
        """Generate genotype JSON field from already set ``self.case``."""
        genotype = {}
        for line in self.case.pedigree:
            if line["affected"] == 2:
                genotype[line["patient"]] = {"gt": "0/1"}
            else:
                genotype[line["patient"]] = {"gt": "0/0"}
        return genotype


PHENOTYPES = ["HP:0001166", "HP:0001049", "HP:0001039", "HP:0000543", "HP:0001249"]


class PhenotypeFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Phenotype`` objects."""

    class Meta:
        model = Phenotype

    case = factory.SubFactory(CaseFactory)
    phenotype = factory.Iterator(PHENOTYPES)


VISIBILITY_LEVEL_MAPPING = {vis: i + 1 for i, vis in enumerate(list(range(0, 25, 5)))}


class ConsortiumFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Consortium`` objects."""

    class Meta:
        model = Consortium

    name = factory.Sequence(lambda n: 'Consortium %d' % n)
    visibility_level = factory.Iterator(list(VISIBILITY_LEVEL_MAPPING.keys()))

    @factory.post_generation
    def projects(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for project in extracted:
                self.projects.add(project)


class RemoteSiteFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``RemoteSite`` objects."""

    class Meta:
        model = RemoteSite

    name = factory.Sequence(lambda n: "Remote Site %d" % n)
    key = factory.Sequence(lambda n: "".join(
        random.choices(string.ascii_lowercase + string.digits + string.ascii_uppercase, k=7)) + "%d" % n)
    access_limit = factory.Sequence(lambda n: (n + 1) * 10)

    @factory.post_generation
    def consortia(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for consortium in extracted:
                self.consortia.add(consortium)


# class LogEntryFactory(factory.django.DjangoModelFactory, RequestFactory):
#    """Factory for creating ``LogEntry`` objects."""

# class Meta:
#   model = LogEntry

# ip_address =
# user_identifier = factory.Sequence(lambda n: "User" % n)
# date_time = factory.LazyFunction(datetime.now)
# authuser = factory.SubFactory(RemoteSiteFactory)

# @factory.lazy_attribute
# def request(self):
#    request = factory.SubFactory(RequestFactory).get
# status_code = request.
# response_size =


class MetadataBeaconFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``MetadataBeacon`` objects."""

    class Meta:
        model = MetadataBeacon

    #: Unique identifier of the beacon. Use reverse domain name notation.
    beacon_id = factory.Sequence(lambda n: "Id %d" % n)
    #: Human readable name of the beacon.
    name = factory.Sequence(lambda n: "Beacon %d" % n)
    #: Version of the API provided by the beacon.
    api_version = factory.Sequence(lambda n: "1.0.%d" % n)


class MetadataBeaconOrganizationFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``MetadataBeaconOrganization`` objects."""

    class Meta:
        model = MetadataBeaconOrganization

    #: Unique identifier of the organization.
    beacon_org_id = factory.Sequence(lambda n: "Id %d" % n)
    #: Name of the organization.
    name = factory.Sequence(lambda n: "Organization %d" % n)
    # : URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an
    # email (RFC 2368 format).
    contact_url = factory.LazyAttribute(lambda obj: '%s.com' % obj.name)
    #: Beacon ID which this organization hosts.
    metadata_beacon = factory.SubFactory(MetadataBeaconFactory)


class MetadataBeaconDatasetFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``MetadataBeaconDataset`` objects."""

    class Meta:
        model = MetadataBeaconDataset

    #: Unique identifier of the dataset.
    beacon_data_id = factory.Sequence(lambda n: "Id %d" % n)
    #: Name of the dataset.
    name = factory.Sequence(lambda n: "Dataset %d" % n)
    #: Assembly identifier.
    assembly_id = "GRCh37"
    #: The time the dataset was created (ISO 8601 format).
    create_date_time = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    #: The time the dataset was updated in (ISO 8601 format).
    update_date_time = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    #: Beacon ID which this organisation hosts.
    metadata_beacon = factory.SubFactory(MetadataBeaconFactory)
