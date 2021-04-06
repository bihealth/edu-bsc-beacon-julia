from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse, HttpResponseBadRequest
from django.views import View
from django.db import models
import re
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
)
from .json_structures import AlleleResponse


class CaseQueryVariant:
    exists = False
    allele_count_greater_ten = False
    allele_count = 0
    coarse_phenotypes = []
    phenotypes = []
    case_indices = []

    def make_query_20(self, variant): ####allele count vs visibility level
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count > 10:
                self.allele_count_greater_ten = True

    def make_query_15(self, variant):
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count > 10:
                self.allele_count_greater_ten = True

    def make_query_10(self, variant):
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count > 10:
                self.allele_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.coarse_phenotypes.append(p.get_coarse_phenotype())

    def make_query_5(self, variant):
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count > 10:
                self.allele_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes.append(p.phenotype)

    def make_query_0(self, variant):
        self.case_indices.append(variant.case.index)
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count > 10:
                self.allele_count_greater_ten = True
            for p in Phenotype.objects.filter(case=variant.case):
                self.phenotypes.append(p.phenotype)
