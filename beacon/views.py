from .models import (
    Variant,
    Phenotype,
    Case,
    Project,
    Consortium,
    ProjectConsortium,
    MetadataBeacon,
    MetadataBeaconOrganisation,
    MetadataBeaconDataset,
)


class JSONResponse():

    def create_info_response(self):
        """

        :rtype: object
         """

    def create_query_response(self):
        """

        :rtype: object
        """


class CaseInfoEndpoint():
    def get(self):
        """

        :rtype: object
        """

    def post(self):
        """

        :rtype: object
        """


class CaseQueryEndpoint():

    def get(self):
        """

        :rtype: object
        """

    def post(self):
        """

        :rtype: object
        """

    def authenticate(self):
        """

        :rtype: object
        """

    def get_filter(self):
        """

        :rtype: object
        """

    def get_log_statistics(self):
        """

        :rtype: object
        """
