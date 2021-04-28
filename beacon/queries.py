from .models import Phenotype


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
        self.internal_allele_count += variant.get_allele_count()
        if self.allele_count + self.internal_allele_count > 10:
            self.allele_count_greater_ten = True

    def make_query_15(self, variant):
        self.allele_count += variant.get_allele_count()
        if self.allele_count + self.internal_allele_count > 10:
            self.allele_count_greater_ten = True

    def make_query_10(self, variant):
        self.allele_count += variant.get_allele_count()
        if self.allele_count + self.internal_allele_count > 10:
            self.allele_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.coarse_phenotypes.append(p.get_coarse_phenotype())

    def make_query_5(self, variant):
        self.allele_count += variant.get_allele_count()
        if self.allele_count + self.internal_allele_count > 10:
            self.allele_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes.append(p.phenotype)

    def make_query_0(self, variant):
        self.case_indices.append(variant.case.index)
        self.allele_count += variant.get_allele_count()
        if self.allele_count + self.internal_allele_count > 10:
            self.allele_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes.append(p.phenotype)
