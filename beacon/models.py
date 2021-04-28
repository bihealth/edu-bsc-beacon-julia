from django.db import models
import networkx
import obonet

HPO_GRAPH_PATH = "http://purl.obolibrary.org/obo/hp.obo"
HPO_GRAPH = obonet.read_obo(HPO_GRAPH_PATH)


class Project(models.Model):
    """
    A SODAR project.
    """
    #: Project title
    title = models.CharField(
        max_length=255, null=True, help_text="Project title"
    )


class Case(models.Model):
    """
    """
    #: The project containing this case.
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE, help_text="Project to which this object belongs.")
    #: Name of this case.
    name = models.CharField(max_length=255)
    #: Index of this case.
    index = models.CharField(max_length=255)
    #: pedigree
    pedigree = models.JSONField()


class Variant(models.Model):
    """
    A VarFish variant.
    """
    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Link to Case ID.
    case = models.ForeignKey(Case, blank=True, null=True, on_delete=models.CASCADE, help_text="Case to which this variant belongs.")
    #: Genotype information as JSONB
    genotype = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["release", "chromosome", "start", "end", "reference", "alternative"])
        ]

    def get_allele_count(self):
        c = 0
        for x in self.case.pedigree:
            c += self.genotype[x["patient"]]["gt"].count("1")
        return c


class Phenotype(models.Model):
    """
    """
    #: Phenotype information using HPO
    phenotype = models.CharField(max_length=255)
    #: Link to case ID.
    case = models.ForeignKey(Case, blank=True, null=True, on_delete=models.CASCADE, help_text="Case to which this phenotype belongs.")

    class Meta:
        indexes = [
            models.Index(fields=["case"])
        ]

    def get_coarse_phenotype(self):
        """"""
        items = networkx.shortest_path_length(HPO_GRAPH, source=self.phenotype).items()
        phenotype_coarse_terms_dict = {d: n for n, d in items}
        #TODO: check 4 is a good depth
        distance = max(phenotype_coarse_terms_dict.keys())-4
        coarse_terms = [n for n, d in items if d == distance]
        if not coarse_terms:
            return self.phenotype
        else:
            return coarse_terms


class Consortium(models.Model):
    """
    """
    VISIBILITY_LEVEL_CHOICES = [
        (0, "Level_case_index_visible"),
        (5, "Level_phenotype_visible"),
        (10, "Level_coarse_phenotype_visible"),
        (15, "Level_allele_count_visible"),
        (20, "Level_allele_count_greater_ten_visible"),
        (25, "Level_exists_visible")
    ]
    #: Name of the consortium.
    name = models.CharField(max_length=255)
    #: Level of visibility of the variant data
    visibility_level = models.IntegerField(choices=VISIBILITY_LEVEL_CHOICES)
    #: The project containing this consortium.
    projects = models.ManyToManyField(Project, blank=True, null=True, help_text="Project to which this object belongs.")


class RemoteSite(models.Model):
    """
    """
    #: Name of the remote site.
    name = models.CharField(max_length=255)
    #: Authentication key
    key = models.CharField(max_length=255, unique=True)
    #: Access limit per day
    access_limit = models.IntegerField()
    #: The consortium containing this remote site.
    consortia = models.ManyToManyField(Consortium, blank=True, null=True, help_text="Consortium to which this object belongs.")


class LogEntry(models.Model):
    """

    """
    #: IP address client
    ip_address = models.GenericIPAddressField(unpack_ipv4=True)
    #: User identifier
    user_identifier = models.CharField(max_length=255, blank=True, null=True)
    #: User (=consortium)
    authuser = models.ForeignKey(RemoteSite, null=True, on_delete=models.CASCADE, help_text="Remote site to which the client belongs to.")
    #: Date and time of request
    date_time = models.DateTimeField()
    #: Request method
    request = models.CharField(max_length=255)
    #: Status code
    status_code = models.IntegerField()
    #: Size response object in bytes
    response_size = models.IntegerField()


class MetadataBeacon(models.Model):
    """
    """
    #: Unique identifier of the beacon. Use reverse domain name notation.
    beacon_id = models.CharField(max_length=255)
    #: Human readable name of the beacon  -	EGA Beacon
    name = models.CharField(max_length=255)
    #: Version of the API provided by the beacon.
    api_version = models.CharField(max_length=255)


class MetadataBeaconOrganization(models.Model):
    """
    """
    #: Unique identifier of the organization.
    beacon_org_id = models.CharField(max_length=255)
    #: Name of the organization.
    name = models.CharField(max_length=255)
    # : URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an
    # email (RFC 2368 format).
    contact_url = models.CharField(max_length=255)
    #: Beacon ID which this organization hosts.
    metadata_beacon = models.ForeignKey(MetadataBeacon, null=True, on_delete=models.CASCADE, help_text="Beacon which this organization "
                                                                                      "hosts.")


class MetadataBeaconDataset(models.Model):
    """
    """
    #: Unique identifier of the dataset.
    beacon_data_id = models.CharField(max_length=255)
    #: Name of the dataset.
    name = models.CharField(max_length=255)
    #: Assembly identifier. 	- "GRCh38"
    assembly_id = models.CharField(max_length=255)
    #: The time the dataset was created (ISO 8601 format). 	- "2012-07-19 or 2017-01-17T20:33:40Z"
    create_date_time = models.DateTimeField()
    #: The time the dataset was updated in (ISO 8601 format). - "2012-07-19 or 2017-01-17T20:33:40Z"
    update_date_time = models.DateTimeField()
    #: Beacon ID which this organisation hosts.
    metadata_beacon = models.ForeignKey(MetadataBeacon, null=True, on_delete=models.CASCADE, help_text="Beacon which this dataset "
                                                                                      "contains.")
