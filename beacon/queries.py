from ipaddress import ip_address
from .models import (
    Phenotype,
    LogEntry,
)


class CaseQueryVariant:

    def __init__(self):
        self.exists = False
        self.allele_count_greater_ten = False
        self.allele_count = 0
        self.internal_allele_count = 0
        self.coarse_phenotypes = []
        self.phenotypes = []
        self.case_indices = []

    def make_query_20(self, variant):
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count_internal += variant.get_allele_count(i)
            if self.allele_count + self.internal_allele_count > 10:
                self.allele_count_greater_ten = True

    def make_query_15(self, variant):
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count + self.internal_allele_count > 10:
                self.allele_count_greater_ten = True

    def make_query_10(self, variant):
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count + self.internal_allele_count > 10:
                self.allele_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.coarse_phenotypes.append(p.get_coarse_phenotype())

    def make_query_5(self, variant):
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count + self.internal_allele_count > 10:
                self.allele_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes.append(p.phenotype)

    def make_query_0(self, variant):
        self.case_indices.append(variant.case.index)
        case_indices = variant.case.get_members()
        for i in case_indices:
            self.allele_count += variant.get_allele_count(i)
            if self.allele_count + self.internal_allele_count > 10:
                self.allele_count_greater_ten = True
            for p in Phenotype.objects.filter(case=variant.case):
                self.phenotypes.append(p.phenotype)


class CaseWriteLogEntry:

    def __init__(self, ip_address, user_identifier,
                 authuser, date_time,
                 request,
                 status_code,
                 response_size):
        self.ip_address = ip_address
        self.user_identifier = user_identifier
        self.authuser = authuser
        self.date_time = date_time
        self.request = request
        self.status_code = status_code
        self.response_size = response_size

    def make_log_entry(self):
        client_address = ip_address(self.ip_address)
        LogEntry(ip_address=self.ip_address, user_identifier=self.user_identifier, authuser=self.authuser,
                 date_time=self.date_time, request=self.request, status_code=self.status_code, response_size=self.response_size).save()

