from django.contrib import admin
from .models import (
    Variant,
    Phenotype,
    Case,
    Project,
    Consortium,
    LogEntry,
    MetadataBeacon,
    MetadataBeaconOrganization,
    MetadataBeaconDataset,
    RemoteSite
)
# Register your models here.
admin.site.register(
    (
        Variant,
        Phenotype,
        Case,
        Project,
        LogEntry,
        MetadataBeacon,
        MetadataBeaconOrganization,
        MetadataBeaconDataset,
        RemoteSite,
        Consortium
    )
)
