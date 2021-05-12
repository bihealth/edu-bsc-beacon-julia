from .models import Phenotype


class CaseQueryVariant:
    """
    A Case for getting and collecting the variant data depending on the visibility level defined by a consortium.
    """

    def __init__(self):
        self.exists = False
        self.sample_count = 0
        self.variant_count_greater_ten = False
        self.variant_count = 0
        self.internal_variant_count = 0
        self.frequency = 0
        self.frequency_count = 0
        self.coarse_phenotypes = set()
        self.phenotypes = set()
        self.case_indices = []

    def make_query_25(self, variant):
        """
        Queries the variant object for visibility level 25 (=public).

        :param variant: A variant object.
        """
        counts = self._get_counts(variant)

    def make_query_20(self, variant):
        """
        Queries the variant object for visibility level 20 which changes the variantCount>10.

        :param variant: A variant object.
        """
        self.internal_variant_count += self._get_counts(variant)
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True

    def make_query_15(self, variant):
        """
        Queries the variant object for visibility level 15 which changes the variantCount>10 and the variantCount.

        :param variant: A variant object.
        """
        self.variant_count += self._get_counts(variant)
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True

    def make_query_10(self, variant):
        """
        Queries the variant object for visibility level 10 which changes the variantCount>10, the variantCount
        and the coarsePhenotype.

        :param variant: A variant object.
        """
        self.variant_count += self._get_counts(variant)
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.coarse_phenotypes = self.coarse_phenotypes.union(
                p.get_coarse_phenotype()
            )

    def make_query_5(self, variant):
        """
        Queries the variant object for visibility level 10 which changes the variantCount>10, the variantCount
        and the phenotype.

        :param variant: A variant object.
        """
        self.variant_count += self._get_counts(variant)
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes = self.phenotypes.union({p.phenotype})

    def make_query_0(self, variant):
        """
        Queries the variant object for visibility level 10 which changes the variantCount>10, the variantCount,
        the phenotype and the caseIndex.

        :param variant: A variant object.
        """
        self.case_indices.append(variant.case.index)
        self.variant_count += self._get_counts(variant)
        if self.variant_count + self.internal_variant_count > 10:
            self.variant_count_greater_ten = True
        for p in Phenotype.objects.filter(case=variant.case):
            self.phenotypes = self.phenotypes.union({p.phenotype})

    def _get_counts(self, variant):
        """
        Counts and changes the sample, frequency and variant count.

        :param variant: A variant object.
        :return: integer of variant counts
        """
        (
            variant_count,
            sample_count,
            frequency_count,
        ) = variant.get_variant_sample_frequency_count()
        self.sample_count += sample_count
        self.frequency_count += frequency_count
        return variant_count
