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

    project = factory.SubFactory(ProjectFactory)
    name = factory.LazyAttributeSequence(
        lambda o, n: "case %03d: %s" % (n, o.structure)
    )
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


CHROMOSOME_MAPPING = {
    str(chrom): i + 1 for i, chrom in enumerate(list(range(1, 23)) + ["X", "Y"])
}


class VariantFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Variant`` objects."""

    class Meta:
        model = Variant

    release = "GRCh37"
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(
        lambda o: o.start + len(o.reference) - len(o.alternative)
    )
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

    name = factory.Sequence(lambda n: "Consortium %d" % n)
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
    key = factory.Sequence(
        lambda n: "".join(
            random.choices(
                string.ascii_lowercase + string.digits + string.ascii_uppercase, k=7
            )
        )
                  + "%d" % n
    )
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


METHOD_MAPPING = {method: i + 1 for i, method in enumerate(["GET", "POST"])}


class LogEntryFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``LogEntry`` objects."""

    class Meta:
        model = LogEntry

    class Params:
        endpoint = "\query"
        exist = True
        chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
        start = factory.Sequence(lambda n: (n + 1) * 100)
        end = factory.LazyAttribute(
            lambda o: o.start + len(o.reference) - len(o.alternative)
        )
        reference = factory.Iterator(["ACGT"])
        alternative = factory.Iterator(["CGTA"])
        method = factory.Iterator(list(METHOD_MAPPING.keys()))
        remote_site = factory.SubFactory(RemoteSiteFactory)

    ip_address = factory.Sequence(lambda n: "100.0.0.%d" % n)
    user_identifier = factory.Sequence(lambda n: "User_%d" % n)
    date_time = factory.fuzzy.FuzzyDateTime(datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc), datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc))
    response_size = 700

    @factory.lazy_attribute
    def status_code(self):
        if self.endpoint is "\query":
            return np.random.choice([200, 403, 400, 401], p=[0.8, 0.15, 0.025, 0.025], size=1)
        else:
            return 200

    @factory.lazy_attribute
    def authuser(self):
        if self.status_code is not 401:
            return self.remote_site
        else:
            return None

    @factory.lazy_attribute
    def request(self):
        if self.endpoint == "\query":
            if (self.status_code is 200) and self.exist:
                request = ("[('referenceName', %s),"
                           " ('start', %d),"
                           " ('end', %d),"
                           " ('referenceBases', %s),"
                           " ('alternateBases', %s)]" % (self.chromosome, self.start, self.end, self.reference, self.alternative))
            elif self.status_code is 400:
                request = ("[('refereceName', %s),"
                           " ('star', %s),"
                           " ('ed', %s),"
                           " ('referenceBase', %s),"
                           " ('altenateBases', %s)]" % (self.chromosome, self.start, self.end, self.reference, self.alternative))
            else:
                request = str([])
            return "%s;/query;%s;HTTP/1.1" % (self.method, request)
        else:
            return "GET;/;HTTP/1.1"

    @factory.post_generation
    def cases(self, create, extracted, **kwargs):
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
