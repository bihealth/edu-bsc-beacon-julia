from django.contrib import admin
import logging

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

# Register your models here.
admin.site.register(
    (
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
)

