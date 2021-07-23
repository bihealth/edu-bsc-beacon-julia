import attr
import typing
from .models import Variant


class QueryResponse:
    """
    The QueryResponseObject defined by the beacon protocol.
    """

    def __init__(
        self,
        beacon_id,
        api_version,
        allele_request,
        exists=None,
        error=None,
        dataset_allele_response=None,
    ):
        self.beacon_id = beacon_id
        self.api_version = api_version
        self.allele_request = allele_request
        self.exists = exists
        self.error = error
        self.dataset_allele_response = dataset_allele_response

    def create_dict(self):
        """
        Creates a dictionary for the JSONResponse.
        
        :return: dict of QueryResponseObject
        """
        if not self.dataset_allele_response:
            self.dataset_allele_response = []
        return dict(
            beaconId=self.beacon_id,
            apiVersion=self.api_version,
            exists=self.exists,
            error=self.error,
            alleleRequest=self.allele_request,
            datasetAlleleResponses=self.dataset_allele_response,
        )


class AlleleRequest:
    """
    The AlleleRequestObject defined by the beacon protocol.
    """

    def __init__(self, chromosome, start, end, reference, alternative, release):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.reference = reference
        self.alternative = alternative
        self.release = release

    def create_dict(self):
        """
        Creates a dictionary for the JSONResponse.
        
        :return: dict of AlleleRequestObject
        """
        return dict(
            referenceName=self.chromosome,
            start=self.start,
            end=self.end,
            referenceBases=self.reference,
            alternateBases=self.alternative,
            assemblyId=self.release,
        )


class Error:
    """
    The ErrorObject defined by the beacon protocol.
    """

    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

    def create_dict(self):
        """
        Creates a dictionary for the JSONResponse.
        
        :return: dict of ErrorObject
        """
        return dict(errorCode=self.error_code, errorMessage=self.error_message)


@attr.s
class AlleleResponse(object):
    """
    An extended AlleleResponseObject defined by the beacon protocol.
    """

    exists: bool = False
    sample_count: int = 0
    variant_count_greater_ten: bool = False
    variant_count: int = 0
    frequency: float = 0
    coarse_phenotype = attr.ib(factory=set)
    phenotype = attr.ib(factory=set)
    case_indices = attr.ib(factory=list)

    def create_dict(self):
        """
        Creates a dictionary for the JSONResponse.
        
        :return: dict of AlleleResponseObject
        """
        allele_response_dict = {
            "exists": self.exists,
            "sampleCount": self.sample_count,
            "variantCount>10": self.variant_count_greater_ten,
            "variantCount": self.variant_count,
            "frequency": self.frequency,
            "coarsePhenotype": sorted(list(self.coarse_phenotype)),
            "phenotype": sorted(list(self.phenotype)),
            "caseName": sorted(self.case_indices),
        }
        return allele_response_dict


@attr.s
class AlleleResponseAccumulation(AlleleResponse):
    """
    A Case for getting and collecting the variant data depending on the visibility level defined by a consortium.
    """

    internal_variant_count: int = 0
    frequency_count: int = 0
    variant: Variant = Variant()


class InfoResponse:
    """
    The InfoResponseObject defined by the beacon protocol.
    """

    def __init__(
        self, beacon_id, name, api_version, dataset_dict_list, organization_dict
    ):
        self.beacon_id = beacon_id
        self.name = name
        self.api_version = api_version
        self.dataset_dict_list = dataset_dict_list
        self.organization_dict = organization_dict

    def create_dict(self):
        """
        Creates a dictionary for the JSONResponse.
        
        :return: dict of InfoResponseObject
        """
        return dict(
            id=self.beacon_id,
            name=self.name,
            apiVersion=self.api_version,
            datasets=self.dataset_dict_list,
            organization=self.organization_dict,
        )


class DatasetResponse:
    """
    The DatasetResponseObject defined by the beacon protocol.
    """

    def __init__(self, id, name, assembly_id, create_date_time, update_date_time):
        self.id = id
        self.name = name
        self.assembly_id = assembly_id
        self.create_date_time = create_date_time
        self.update_date_time = update_date_time

    def create_dict(self):
        """
        Creates a dictionary for the JSONResponse.
        
        :return: dict of DatasetResponseObject
        """
        return dict(
            id=self.id,
            name=self.name,
            assemblyId=self.assembly_id,
            createDateTime=str(self.create_date_time),
            updateDateTime=str(self.update_date_time),
        )


class OrganizationResponse:
    """
    The OrganizationResponseObject defined by the beacon protocol.
    """

    def __init__(self, id, name, contact_url):
        self.id = id
        self.name = name
        self.contact_url = contact_url

    def create_dict(self):
        """
        Creates a dictionary for the JSONResponse.
        
        :return: dict of OrganizationResponseObject
        """
        return dict(id=self.id, name=self.name, contactUrl=self.contact_url)
