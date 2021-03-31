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

    def __init__(self, consortium_id, chromosome, start, end, reference, alternative, release):
        self.consortium_id = consortium_id
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.reference = reference
        self.alternative = alternative
        self.release = release
        self.variants = Variant.objects.filter(chromosome=self.chromosome,
                                               start=self.start,
                                               reference=self.reference,
                                               end=self.end,
                                               alternative=self.alternative,
                                               release=self.release,
                                               case__project__consortium=self.consortium_id
                                               )
        self.exists = False
        self.allele_count_greater_ten = False
        self.allele_count = 0
        self.coarse_phenotypes = []
        self.phenotypes = []
        self.case_names = []

    def make_query_25(self):
        if not list(self.variants):
            pass
        else:
            self.exists = True
        return AlleleResponse(self.exists,
                              self.allele_count_greater_ten,
                              self.allele_count,
                              self.coarse_phenotypes,
                              self.phenotypes,
                              self.case_names).query_dict_25()

    def make_query_20(self):
        for v in self.variants:
            self.exists = True
            case_index = Case.objects.filter(id=v.case.id).values("index")
            self.allele_count += v.get_allele_count(case_index[0]["index"])
            if self.allele_count > 10:
                self.allele_count_greater_ten = True
                break
        return AlleleResponse(self.exists,
                              self.allele_count_greater_ten,
                              self.allele_count,
                              self.coarse_phenotypes,
                              self.phenotypes,
                              self.case_names).query_dict_20()

    def make_query_15(self):
        for v in self.variants:
            self.exists = True
            case_index = Case.objects.filter(id=v.case.id).values("index")
            self.allele_count += v.get_allele_count(case_index[0]["index"])
        return AlleleResponse(self.exists,
                              self.allele_count_greater_ten,
                              self.allele_count,
                              self.coarse_phenotypes,
                              self.phenotypes,
                              self.case_names).query_dict_15()

    def make_query_10(self):
        for v in self.variants:
            self.exists = True
            case_index = Case.objects.filter(id=v.case.id).values("index")
            self.allele_count += v.get_allele_count(case_index[0]["index"])
            for p in Phenotype.objects.filter(case=v.case):
                self.coarse_phenotypes.append(p.get_coarse_phenotype())
        return AlleleResponse(self.exists,
                              self.allele_count_greater_ten,
                              self.allele_count,
                              self.coarse_phenotypes,
                              self.phenotypes,
                              self.case_names).query_dict_10()

    def make_query_5(self):
        for v in self.variants:
            self.exists = True
            case_index = Case.objects.filter(id=v.case.id).values("index")
            self.allele_count += v.get_allele_count(case_index[0]["index"])
            for p in Phenotype.objects.filter(case=v.case):
                self.phenotypes.append(p)
        return AlleleResponse(self.exists,
                              self.allele_count_greater_ten,
                              self.allele_count,
                              self.coarse_phenotypes,
                              self.phenotypes,
                              self.case_names).query_dict_5()

    def make_query_0(self):
        for v in self.variants:
            self.exists = True
            case = Case.objects.filter(id=v.case.id)
            self.allele_count += v.get_allele_count(case.case_index)
            for p in Phenotype.objects.filter(case=v.case):
                self.phenotypes.append(p)
            self.case_names.append(case.name)
        return AlleleResponse(self.exists,
                              self.allele_count_greater_ten,
                              self.allele_count,
                              self.coarse_phenotypes,
                              self.phenotypes,
                              self.case_names).query_dict_0()
