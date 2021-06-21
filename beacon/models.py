from django.db import models
import networkx
from mysite.settings import HPO_COARSE_TERMS, HPO_GRAPH

class Project(models.Model):
    """
    A SODAR project.
    """

    #: Project title
    title = models.CharField(
        max_length=255, null=True, unique=True, help_text="Project title"
    )


class Case(models.Model):
    """
    A Case as used in VarFish or SODAR.
    """

    #: Project containing this case
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="Project to which this object belongs.",
    )
    #: Name of this case
    name = models.CharField(max_length=255, unique=True)
    #: Index of this case
    index = models.CharField(max_length=255, unique=True)
    #: Pedigree containing information about the case family
    pedigree = models.JSONField()


class Variant(models.Model):
    """
    A VarFish variant.
    """

    CHROMOSOME_CHOICES = [
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
        (11, "11"),
        (12, "12"),
        (13, "13"),
        (14, "14"),
        (15, "15"),
        (16, "16"),
        (17, "17"),
        (18, "18"),
        (19, "19"),
        (20, "20"),
        (21, "21"),
        (22, "22"),
        (23, "X"),
        (24, "Y"),
    ]
    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates, the reference chromosome
    chromosome = models.IntegerField(choices=CHROMOSOME_CHOICES)
    #: Variant coordinates, the 1-based start position
    start = models.IntegerField()
    #: Variant coordinates, the end position
    end = models.IntegerField()
    #: Variant coordinates, the reference base
    reference = models.CharField(max_length=512)
    #: Variant coordinates, the alternate base
    alternative = models.CharField(max_length=512)
    #: Link to Case ID
    case = models.ForeignKey(
        Case,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="Case to which this variant belongs.",
    )
    #: Genotype information as JSONB
    genotype = models.JSONField()

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "release",
                    "chromosome",
                    "start",
                    "end",
                    "reference",
                    "alternative",
                ]
            )
        ]

    def get_variant_sample_frequency_count(self):
        """
        Counts the alleles, samples and total number of alleles for the frequency.

        :return: integer of number of alleles, samples and total numbers of alleles
        """
        c_variant = 0
        c_sample = 0
        c_frequency = 0
        for x in self.case.pedigree:
            allele_count = self.genotype[x["patient"]]["gt"].count("1")
            c_variant += allele_count
            if allele_count > 0:
                c_sample += 1
                if (self.chromosome == 23 and x["sex"] == 1) or (
                    self.chromosome == 24
                ):  # 23: X, 24:Y
                    c_frequency += 1
                else:
                    c_frequency += 2
        return c_variant, c_sample, c_frequency


class Phenotype(models.Model):
    """
    The Phenotype of a case.
    """

    #: Phenotype information using HPO
    phenotype = models.CharField(max_length=255)
    #: Link to case ID
    case = models.ForeignKey(
        Case,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="Case to which this phenotype belongs.",
    )

    class Meta:
        indexes = [models.Index(fields=["case"])]

    def get_coarse_phenotype(self):
        """
        Returns a coarse term of the phenotype from the Human Phenotype Ontology.

        :return: Set of phenotype terms
        """
        # get already created graph for HPO (Human Phenotype Ontology)
        # intersect with ancestor nodes from phenotype
        coarse_phenotypes = networkx.algorithms.ancestors(
            HPO_GRAPH, self.phenotype
        ).intersection(HPO_COARSE_TERMS)
        # if phenotype is already a coarse term
        if coarse_phenotypes == set():
            return {self.phenotype}
        else:
            return coarse_phenotypes


class Consortium(models.Model):
    """
    A Consortium related to certain Remote Sites and Projects.
    Indicates the visibility level of the project variant data which is requested.
    """

    VISIBILITY_LEVEL_CHOICES = [
        (0, "Level_case_index_visible"),
        (5, "Level_phenotype_visible"),
        (10, "Level_coarse_phenotype_visible"),
        (15, "Level_variant_count_visible"),
        (20, "Level_variant_count_greater_ten_visible"),
        (25, "Level_exists_sample_count_visible"),
    ]
    #: Name of the consortium
    name = models.CharField(max_length=255, unique=True)
    #: Level of visibility of the variant data
    visibility_level = models.IntegerField(choices=VISIBILITY_LEVEL_CHOICES)
    #: The project containing this consortium
    projects = models.ManyToManyField(
        Project, blank=True, help_text="Project to which this object belongs."
    )


class RemoteSite(models.Model):
    """
    A Remote Site for which the client needs a key to log into.
    The access of the Remote Site can be regulated by a given limit.
    """

    #: Name of the remote site
    name = models.CharField(max_length=255, unique=True)
    #: Authentication key
    key = models.CharField(max_length=255, unique=True)
    #: Access limit per day
    access_limit = models.IntegerField()
    #: The consortium containing this remote site
    consortia = models.ManyToManyField(
        Consortium, blank=True, help_text="Consortium to which this object belongs."
    )


class LogEntry(models.Model):
    """
    Each requests of the Beacon are logged with a LogEntry object.
    """

    #: IP address client
    ip_address = models.GenericIPAddressField(unpack_ipv4=True)
    #: User identifier passed by X-Remote-Site header
    user_identifier = models.CharField(max_length=255, blank=True, null=True)
    #: User (=RemoteSite)
    remote_site = models.ForeignKey(
        RemoteSite,
        null=True,
        on_delete=models.CASCADE,
        help_text="Remote site to which the client belongs to.",
    )
    #: Date and time of request
    date_time = models.DateTimeField()
    #: Request method
    method = models.CharField(max_length=255)
    #: Requested endpoint
    endpoint = models.CharField(max_length=255)
    #: server protocol
    server_protocol = models.CharField(max_length=255)
    #: Status code
    status_code = models.IntegerField()
    #: Size response object in bytes
    response_size = models.IntegerField()
    #: Queried cases to which the variant data belongs to
    cases = models.ManyToManyField(
        Case, blank=True, help_text="Case with request variant."
    )
    #: Requested genome build
    release = models.CharField(max_length=32, null=True)
    #: Requested variant coordinates, the reference chromosome
    chromosome = models.CharField(max_length=255, null=True)
    #: Requested variant coordinates, the 0-based start position
    start = models.IntegerField(null=True)
    #: Requested variant coordinates, the end position
    end = models.IntegerField(null=True)
    #: Requested variant coordinates, the reference base
    reference = models.CharField(max_length=512, null=True)
    #: Requested variant coordinates, the alternate base
    alternative = models.CharField(max_length=512, null=True)


class MetadataBeacon(models.Model):
    """
    The metadata of the beacon.
    """

    #: Unique identifier of the beacon, use reverse domain name notation
    beacon_id = models.CharField(max_length=255)
    #: Human readable name of the beacon
    name = models.CharField(max_length=255)
    #: Version of the API provided by the beacon
    api_version = models.CharField(max_length=255)


class MetadataBeaconOrganization(models.Model):
    """
    The metadata of the organization which hosts the beacon.
    """

    #: Unique identifier of the organization
    beacon_org_id = models.CharField(max_length=255)
    #: Name of the organization
    name = models.CharField(max_length=255)
    #: URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an
    # email (RFC 2368 format)
    contact_url = models.CharField(max_length=255)
    #: Beacon ID which this organization hosts
    metadata_beacon = models.ForeignKey(
        MetadataBeacon,
        null=True,
        on_delete=models.CASCADE,
        help_text="Beacon which this organization " "hosts.",
    )


class MetadataBeaconDataset(models.Model):
    """
    The metadata of the datasets which are contained in the beacon database.
    """

    #: Unique identifier of the dataset
    beacon_data_id = models.CharField(max_length=255)
    #: Name of the dataset
    name = models.CharField(max_length=255)
    #: Assembly identifier
    assembly_id = models.CharField(max_length=255)
    #: The time the dataset was created (ISO 8601 format)
    create_date_time = models.DateTimeField()
    #: The time the dataset was updated in (ISO 8601 format)
    update_date_time = models.DateTimeField()
    #: Beacon ID which this organisation hosts
    metadata_beacon = models.ForeignKey(
        MetadataBeacon,
        null=True,
        on_delete=models.CASCADE,
        help_text="Beacon which this dataset " "contains.",
    )
