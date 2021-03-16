from django.db import models


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
    case_id = models.ForeignKey(Case, help_text="Case to which this variant belongs.")
    #: Genotype information as JSONB
    genotype = JSONField()

    class Meta:
        indexes = [
            models.Index(fields=["release", "chromosome", "start", "end", "reference", "alternative"])
        ]


class Phenotype(models.Model):
    """
    """
    #: Phenotype information using HPO
    phenotype = models.CharField()
    #: Link to case ID.
    case_id = models.ForeignKey(Case, help_text="Case to which this phenotype belongs.")


class Case(models.Model):
    """
    """
    #: The project containing this case.
    project = models.ForeignKey(Project, help_text="Project to which this object belongs.")
    #: Name of this case.
    name = models.CharField()
    #: Index of this case.
    index = models.IntegerField()
    #: pedigree 
    pedigree = JSONField()


class Project(models.Model):
    """
    A SODAR project.
    """
    #: Project title
    title = models.CharField(
        max_length=255, unique=False, help_text="Project title"
    )


class Consortium(models.Model):
    """
    """
    #: Name of the consortium.
    name = models.CharField()
    #: Authentication key
    key = models.CharField()
    #: Level of visibility of the variant data
    visibility_level = models.CharField()
    #: Access limit per day
    access_limit = models.IntegerField()


class ProjectConsortium(models.Model):
    """
    """
    #: The project containing this consortium.
    project_id = models.ForeignKey(Project, help_text="Project to which this object belongs.")
    #: The consortium containing this project.
    consortium_id = models.ForeignKey(Consortium, help_text="Consortium to which this object belongs.")


class MetadataBeacon(models.Model):
    """
    """
    #: Unique identifier of the beacon. Use reverse domain name notation.
    beacon_id = models.CharField()
    #: Human readable name of the beacon  -	EGA Beacon
    name = models.CharField()
    #: Version of the API provided by the beacon.
    api_version = models.CharField()


class MetadataBeaconOrganisation(models.Model):
    """
    """
    #: Unique identifier of the organization.
    beacon_org_id = models.CharField()
    #: Name of the organization.	
    name = models.CharField()
    # : URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an
    # email (RFC 2368 format).
    contact_url = models.CharField()
    #: Beacon ID which this organisation hosts. 
    beacon_id = models.ForeignKey(MetadataBeacon, help_text="Beacon which this organisation hosts.")


class MetadataBeaconDataset(models.Model):
    """
    """
    #: Unique identifier of the dataset.
    beacon_data_id = models.CharField()
    #: Name of the dataset.	
    name = models.CharField()
    #: Assembly identifier 	- "GRCh38"
    assembly_id = models.CharField()
    #: The time the dataset was created (ISO 8601 format). 	- "2012-07-19 or 2017-01-17T20:33:40Z"
    create_date_time = models.CharField()
    #: The time the dataset was updated in (ISO 8601 format). - "2012-07-19 or 2017-01-17T20:33:40Z"
    update_date_time = models.CharField()
    #: Beacon ID which this organisation hosts. 
    beacon_id = models.ForeignKey(MetadataBeacon, help_text="Beacon which this organisation hosts.")
