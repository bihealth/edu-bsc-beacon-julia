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
    # case_id = models.IntegerField()
    case_id = models.ForeignKey(Case, help_text="Case to which this variant belongs")
    #: Genotype information as JSONB
    genotype = JSONField()

class Phenotype(models.Model):
    """
    """
    #: Phenotype information using HPO
    phenotype = models.CharField()
    #: Link to Case ID.
    case_id = models.ForeignKey(Case, help_text="Case to which this phenotype belongs")
    

class Case(models.Model):
    """
    """
    #: The project containing this case.
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")
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
        max_length=255, unique=False, help_text='Project title'
    )

class Consortium(models.Model):
    """
    """
    #: Name of the consortium.
    name = models.CharField()
    #: Authentification Key
    key = models.CharField()
    #: Level of visability of the variant data
    visability_level = models.CharField()
    #: Acces limit per day
    accesLimit = models.IntegerField()

class ProjectConsortium(models.Model):
    """
    """
    #: The project containing this consortium.
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")
    #: The consortium containing this project.
    project = models.ForeignKey(Consortium, help_text="Project in which this objects belongs")


class MetadataBeacon(models.Model):
    """
    """
    #: Unique identifier of the beacon. Use reverse domain name notation.
    beacon_id  = models.CharField()
    #: Human readable name of the beacon  -	EGA Beacon
    name = models.CharField()
    #: Version of the API provided by the beacon.
    apiVersion = models.CharField()
    #: Description of the beacon. -- "This sample set comprises cases of schizophrenia with additional cognitive measurements, collected in Aberdeen, Scotland."
    description = models.CharField() 
    #: Version of the Beacon server instance. - v0.1
    version = models.CharField()
    #: 	URL to the welcome page for this beacon (RFC 3986 format). - 'http://example.org/wiki/Main_Page'
    welcomeUrl = models.CharField()
    #:  Alternative URL to the API, e.g. a restricted version of this beacon (RFC 3986 format). - 'http://example.org/wiki/Main_Page'	
    alternativeUrl = models.CharField()
    #: The time the beacon was created (ISO 8601 format). -	'2012-07-19 or 2017-01-17T20:33:40Z' 
    createDateTime = models.CharField()
    #: The time the beacon was updated in (ISO 8601 format). -	'2012-07-19 or 2017-01-17T20:33:40Z'
    updateDateTime = models.CharField()
    #:	Examples of interesting queries, e.g. a few queries demonstrating different responses. 	array 	Array of BeaconAlleleRequest objects (see Query endpoint request)
    sampleAlleleRequests = JSONField()
    #: 'Additional structured metadata, key-value pairs.' 
    info =	JSONField()

class MetadataBeaconOrganisation(models.Model):
    """
    """
    #:Unique identifier of the organization.
    beaconOrg_id = models.CharField()
    #: Name of the organization.	
    name = models.CharField()
    #: Description of the organization.
    description = models.CharField()
    #: Address of the organization.	
    address = models.CharField()
    #: URL of the website of the organization (RFC 3986 format).
    welcomeUrl = models.CharField()	
    #: URL with the contact for the beacon operator/maintainer, e.g. link to a contact form (RFC 3986 format) or an email (RFC 2368 format). 	string 	-
    contactUrl = models.CharField()
    #: URL to the logo (PNG/JPG format) of the organization (RFC 3986 format). 
    logoUrl = models.CharField()
    #: Additional structured metadata, key-value pairs. 
    info = models.CharField()
    #: Beacon ID which this organisation hosts. 
    beacon_id = models.ForeignKey(MetadataBeacon, help_text="Beacon which this organisation hosts.")

class MetadataBeaconDataset(models.Model):
    """
    """
    #: Unique identifier of the dataset.
    beaconData_id = models.CharField()
    #: Name of the dataset.	
    name = models.CharField()
    #: Assembly identifier 	- 'GRCh38'	
    assemblyId = models.CharField()	
    #: The time the dataset was created (ISO 8601 format). 	- '2012-07-19 or 2017-01-17T20:33:40Z' 
    createDateTime = models.CharField()
    #: The time the dataset was updated in (ISO 8601 format). - '2012-07-19 or 2017-01-17T20:33:40Z'
    updateDateTime = models.CharField()
    #: Description of the dataset. 
    description = models.CharField() 
    #: Version of the dataset. -	v0.1
    version = models.CharField()
    #: Total number of variants in the dataset. - 230453
    variantCount = models.IntegerField()
    #: Total number of calls in the dataset. - 213454
    callCount = models.IntegerField()
    #: Total number of samples in the dataset. - 13	
    sampleCount = models.IntegerField()
    #: URL to an external system providing more dataset information (RFC 3986 format). 
    externalUrl = models.CharField()
    #: Additional structured metadata, key-value pairs.
    info = JSONField()
    #: Beacon ID which this organisation hosts. 
    beacon_id = models.ForeignKey(MetadataBeacon, help_text="Beacon which this organisation hosts.")

class DataUseConditions(models.Model):
    """
    """
    #: The consent code for the use of data. 	object 	See GA4GH-CC
    consentCodeDataUse = models.CharField()	
    #: AdamDataUse ID which apllies for this data conditions. 
    AdamDataUse_id = models.ForeignKey(AdamDataUse_id, help_text="ADA-M which apllies for the conditions.")
    #: BeaconDataset ID which this organisation hosts. 
    beaconData_id = models.ForeignKey(MetadataBeaconDataset, help_text="Dataset to which the conditions apply for.")

class AdamDataUse(models.Model):
    """
    """
     #: AdamDataUse ID which apllies for this data conditions. 
    AdamDataUse_id = models.CharField()
    #:	General description of what the data is. 	object 	See ADA-M
    header = JSONField()
    #: Profile of the data. 	object 	See ADA-M
    profile = JSONField() 
    #: Terms related to the use of the data. 	object 	See ADA-M
    terms = JSONField()
    #: 	Special conditions. 	object 	See ADA-M
    metaConditions = JSONField()	