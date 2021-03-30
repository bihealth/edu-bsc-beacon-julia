from django.db import models
import networkx
import obonet


class Project(models.Model):
    """
    A SODAR project.
    """
    #: Project title
    title = models.CharField(
        max_length=255, unique=False, help_text="Project title"
    )


class Case(models.Model):
    """
    """
    #: The project containing this case.
    project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text="Project to which this object belongs.")
    #: Name of this case.
    name = models.CharField(max_length=255)
    #: Index of this case.
    index = models.CharField(max_length=255)
    #: pedigree
    pedigree = models.JSONField()

    def get_members(self):
        """Return list of members in ``pedigree``."""
        return sorted([x["patient"] for x in self.pedigree])


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
    case = models.ForeignKey(Case, on_delete=models.CASCADE, help_text="Case to which this variant belongs.")
    #: Genotype information as JSONB
    genotype = models.JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["release", "chromosome", "start", "end", "reference", "alternative"])
        ]

    def get_allele_count(self, case_index):
        return self.genotype[case_index]["gt"].count("1")


class Phenotype(models.Model):
    """
    """
    #: Phenotype information using HPO
    phenotype = models.CharField(max_length=255)
    #: Link to case ID.
    case = models.ForeignKey(Case, on_delete=models.CASCADE, help_text="Case to which this phenotype belongs.")

    class Meta:
        indexes = [
            models.Index(fields=["case"])
        ]

    def get_coarse_phenotype(self, url="http://purl.obolibrary.org/obo/hp.obo"):
        """"""
        try:
            hpo_graph = obonet.read_obo(url)
            phenotype_superterms = list(networkx.descendants(hpo_graph, self.phenotype))
            if len(phenotype_superterms) > 4:
                return phenotype_superterms[4]
            else:
                return self.phenotype
        except (ValueError, networkx.exception.NetworkXError, KeyError):
            return None


class Consortium(models.Model):
    """
    """
    #: Name of the consortium.
    name = models.CharField(max_length=255)
    #: Authentication key
    key = models.CharField(max_length=255)
    #: Level of visibility of the variant data
    visibility_level = models.CharField(max_length=255)
    #: Access limit per day
    access_limit = models.IntegerField()
    #: The project containing this consortium.
    projects = models.ManyToManyField(Project, help_text="Project to which this object belongs.")


class RemoteSide(models.Model):
    """
    """
    #: Name of the remote side.
    name = models.CharField(max_length=255)
    #: Authentication key
    key = models.CharField(max_length=255)
    #: Level of visibility of the variant data
    visibility_level = models.CharField(max_length=255)
    #: Access limit per day
    access_limit = models.IntegerField()
    #: The consortium containing this remote side.
    consortium = models.ManyToManyField(Consortium, help_text="Consortium to which this object belongs.")


class LogEntry(models.Model):
    """

    """
    #: IP address client
    ip_address = models.CharField(max_length=15)
    #: User identifier
    user_identifier = models.CharField(max_length=255)
    #: User (=consortium)
    authuser = models.ForeignKey(Consortium, on_delete=models.CASCADE, help_text="Consortium to which the client belongs to.")
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
    beacon_id = models.ForeignKey(MetadataBeacon, on_delete=models.CASCADE, help_text="Beacon which this organization "
                                                                                      "hosts.")


class MetadataBeaconDataset(models.Model):
    """
    """
    #: Unique identifier of the dataset.
    beacon_data_id = models.CharField(max_length=255)
    #: Name of the dataset.
    name = models.CharField(max_length=255)
    #: Assembly identifier 	- "GRCh38"
    assembly_id = models.CharField(max_length=255)
    #: The time the dataset was created (ISO 8601 format). 	- "2012-07-19 or 2017-01-17T20:33:40Z"
    create_date_time = models.DateTimeField()
    #: The time the dataset was updated in (ISO 8601 format). - "2012-07-19 or 2017-01-17T20:33:40Z"
    update_date_time = models.DateTimeField()
    #: Beacon ID which this organisation hosts.
    beacon_id = models.ForeignKey(MetadataBeacon, on_delete=models.CASCADE, help_text="Beacon which this dataset "
                                                                                      "contains.")
