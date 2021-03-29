from django.contrib import admin

# Register your models here.
from django.contrib import admin
import logging

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
    RemoteSide
)

# Register your models here.
admin.site.register(
    (
        Variant,
        Phenotype,
        Case,
        Project,
        Consortium,
        LogEntry,
        MetadataBeacon,
        MetadataBeaconOrganization,
        MetadataBeaconDataset,
        RemoteSide
    )
)
