from .models import Phenotype


class CaseQueryVariant:

    def __init__(self):
        self.exists = False
        self.sample_count = 0
        self.variant_count_greater_ten = False
        self.variant_count = 0
        self.internal_variant_count = 0
        self.frequency = 0
        self.coarse_phenotypes = set()
        self.phenotypes = set()
        self.case_indices = []

    def make_query_25(self, variant):
        internal_variant_count, sample_count = variant.get_variant_sample_count()
        self.sample_count += sample_count

    def make_query_20(self, variant):
        internal_variant_count, sample_count = variant.get_variant_sample_count()
        self.internal_variant_count += internal_variant_count
        self.sample_count += sample_count
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True

    def make_query_15(self, variant):
        variant_count, sample_count = variant.get_variant_sample_count()
        self.variant_count += variant_count
        self.sample_count += sample_count
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True

    def make_query_10(self, variant):
        variant_count, sample_count = variant.get_variant_sample_count()
        self.variant_count += variant_count
        self.sample_count += sample_count
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.coarse_phenotypes = self.coarse_phenotypes.union(p.get_coarse_phenotype())

    def make_query_5(self, variant):
        variant_count, sample_count = variant.get_variant_sample_count()
        self.variant_count += variant_count
        self.sample_count += sample_count
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes = self.phenotypes.union({p.phenotype})

    def make_query_0(self, variant):
        self.case_indices.append(variant.case.index)
        variant_count, sample_count = variant.get_variant_sample_count()
        self.variant_count += variant_count
        self.sample_count += sample_count
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes = self.phenotypes.union({p.phenotype})
