import factory
from factory import fuzzy
from django.utils import timezone
import numpy as np
import datetime
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

    #: The title of the project
    title = factory.Sequence(lambda n: "Project %d" % n)


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

    #: The project to which the case belongs
    project = factory.SubFactory(ProjectFactory)
    #: The name of the case
    name = factory.LazyAttributeSequence(
        lambda o, n: "case %03d: %s" % (n, o.structure)
    )
    #: The index of the case
    index = factory.Sequence(lambda n: "index_%03d-N1-DNA1-WES1" % n)

    #: The pedigree of the case
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


CHROMOSOME_MAPPING = {
    str(chrom): i + 1 for i, chrom in enumerate(list(range(1, 24)))
}


class VariantFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Variant`` objects."""

    class Meta:
        model = Variant

    #: The reference genome of the variant
    release = "GRCh37"
    #: The chromosome of the variant
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    #: The start position of the variant, 1-based
    start = factory.Sequence(lambda n: (n + 1) * 100)
    #: The end position of the variant, 1-based
    end = factory.LazyAttribute(
        lambda o: o.start + len(o.reference) - len(o.alternative)
    )
    #: The reference base of the variant
    reference = factory.Iterator("ACGT")
    #: The alternate base of the variant
    alternative = factory.Iterator("CGTA")
    #: The case to which the variant belongs to
    case = factory.SubFactory(CaseFactory)

    #: The genotype of the variant
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

    #: The case to which the phenotype belongs to
    case = factory.SubFactory(CaseFactory)
    #: HPO (Human Phenotype Ontology) term
    phenotype = factory.Iterator(PHENOTYPES)


VISIBILITY_LEVEL_MAPPING = {vis: i + 1 for i, vis in enumerate(list(range(0, 25, 5)))}


class ConsortiumFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Consortium`` objects."""

    class Meta:
        model = Consortium

    #: The name of the consortium
    name = factory.Sequence(lambda n: "Consortium %d" % n)
    #: The visibility level of the consortium with the following options: 0, 5, 10, 15, 20, 25
    visibility_level = factory.Iterator(list(VISIBILITY_LEVEL_MAPPING.keys()))

    #: The projects to which the consortium has access to
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

    #: The name of the remote site
    name = factory.Sequence(lambda n: "Remote Site %d" % n)
    #: The key used for authentication
    key = factory.Sequence(
        lambda n: "".join(
            random.choices(
                string.ascii_lowercase + string.digits + string.ascii_uppercase, k=7
            )
        )
        + "%d" % n
    )
    #: The daily access limit how often a beacon can get queried from remote site
    access_limit = factory.Sequence(lambda n: (n + 1) * 10)

    #: The consortia to which the remote site belongs to
    @factory.post_generation
    def consortia(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return
        if extracted:
            # A list of groups were passed in, use them
            for consortium in extracted:
                self.consortia.add(consortium)


METHOD_MAPPING = {method: i + 1 for i, method in enumerate(["GET", "POST"])}
np.random.seed(100)


class LogEntryFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``LogEntry`` objects."""

    class Meta:
        model = LogEntry

    #: The release passed by the beacon query request
    release = "GRCh37"
    #: The chromosome passed by the beacon query request
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    #: The start position passed by the beacon query request, 1-based
    start = factory.Sequence(lambda n: (n + 1) * 100)
    #: The end position passed by the beacon query request, 1-based
    end = factory.LazyAttribute(
        lambda o: o.start + len(o.reference) - len(o.alternative)
    )
    #: The reference base passed by the beacon query request
    reference = factory.Sequence(lambda n: "ACGT"[n % 4])
    #: The alternate base passed by the beacon query request
    alternative = factory.Sequence(lambda n: "CGTA"[n % 4])
    #: The requesting remote site
    #: None in case of info endpoint and failed authentication
    remote_site = factory.Maybe(
        factory.LazyAttribute(
            lambda o: (o.status_code == 401) or (o.endpoint == "info")
        ),
        None,
        factory.SubFactory(RemoteSiteFactory),
    )
    #: The ip address of the requester
    ip_address = factory.Sequence(lambda n: "100.0.0.%d" % n)
    #: The user name of the requester
    user_identifier = factory.Sequence(lambda n: "User_%d" % n)
    #: The time and date when requested
    date_time = factory.fuzzy.FuzzyDateTime(
        datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
        datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc),
    )
    #: The response size of the response
    response_size = 700
    #: The requested endpoint
    endpoint = factory.Sequence(lambda n: ["query", "info"][n % 2])
    #: The used server protocol
    server_protocol = "HTTP/1.1"
    #: The used REST method
    method = factory.LazyAttributeSequence(
        lambda o, n: ["GET", "POST"][n % 2] if o.endpoint == "query" else "GET"
    )

    #: The status code of the response
    @factory.lazy_attribute
    def status_code(self):
        if self.endpoint == "query":
            return np.random.choice(
                [200, 403, 400, 401], p=[0.8, 0.15, 0.025, 0.025], size=1
            )[0]
        else:
            return 200

    #: The cases which were queried by request
    @factory.post_generation
    def cases(self, create, extracted, **kwargs):
        if (self.endpoint == "info") or (self.status_code != 200):
            return
        else:
            if not create:
                return
            if extracted:
                for case in extracted:
                    self.cases.add(case)


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
    #: URL with the contact for the beacon operator/maintainer,
    # e.g. link to a contact form (RFC 3986 format) or an email (RFC 2368 format).
    contact_url = factory.LazyAttribute(lambda obj: "%s.com" % obj.name)
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
    create_date_time = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
    #: The time the dataset was updated in (ISO 8601 format).
    update_date_time = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
    #: Beacon ID which this organisation hosts.
    metadata_beacon = factory.SubFactory(MetadataBeaconFactory)
