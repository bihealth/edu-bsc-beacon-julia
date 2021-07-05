from .models import Phenotype
from abc import ABC, abstractmethod


class VariantAccumulator(ABC):
    """
    The accumulator class declares the factory method accumulate_variant.
    The accumulator's subclasses provide the implementation of this method.
    """

    @abstractmethod
    def accumulate_variant(self, allele_response):
        """
        Abstract method for the accumulation the information about the
        AlleleResponseAccumulation object variant.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        pass

    def accumulate(self, allele_response):
        """
        Call method for the accumulation factory method to accumulate information
        about the AlleleResponseAccumulation object variant.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        self.accumulate_variant(allele_response)


class VariantAccumulator25(VariantAccumulator):
    """
    Accumulator class for visibility level 25: accumulates information about existence,
    frequency count and sample count.
    """

    def accumulate_variant(self, allele_response):
        """
        Accumulates the information about the AlleleResponseAccumulation object variant
        for visibility level 25 (=public).

        :param allele_response: An AlleleResponseAccumulation object.
        """
        super(VariantAccumulator25, self).accumulate_variant(allele_response)
        allele_response.exists = True
        counts = allele_response.variant.get_variant_sample_frequency_count()
        allele_response.sample_count += counts[1]
        allele_response.frequency_count += counts[2]


class VariantAccumulator20Internal(VariantAccumulator25):
    """
    Accumulator class for visibility level 20: accumulates information about existence,
    frequency count, sample count and variantCount>10.
    """

    def accumulate_variant(self, allele_response):
        """
        Accumulates the information about the AlleleResponseAccumulation object variant
        for visibility level 20 which changes the variantCount>10.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        super(VariantAccumulator20Internal, self).accumulate_variant(allele_response)
        if allele_response.variant_count + allele_response.internal_variant_count > 10:
            allele_response.variant_count_greater_ten = True


class VariantAccumulator20(VariantAccumulator20Internal):
    """
    Accumulator class for visibility level 20: accumulates information about existence,
    frequency count, sample count, internal variant count and variantCount>10.
    """

    def accumulate_variant(self, allele_response):
        """
        Accumulates the information about the AlleleResponseAccumulation object variant
        for visibility level 20 which changes the internal variant count.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        allele_response.internal_variant_count += (
            allele_response.variant.get_variant_sample_frequency_count()[0]
        )
        super(VariantAccumulator20, self).accumulate_variant(allele_response)


class VariantAccumulator15(VariantAccumulator20Internal):
    """
    Accumulator class for visibility level 15: accumulates information about existence,
    frequency count, sample count, allele count and variantCount>10.
    """

    def accumulate_variant(self, allele_response):
        """
        Accumulates the information about the AlleleResponseAccumulation object variant
        for visibility level 15 which changes the variant count.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        allele_response.variant_count += (
            allele_response.variant.get_variant_sample_frequency_count()[0]
        )
        super(VariantAccumulator15, self).accumulate_variant(allele_response)


class VariantAccumulator10(VariantAccumulator15):
    """
    Accumulator class for visibility level 10: accumulates information about existence,
    frequency count, sample count, variantCount>10, allele count and coarse phenotype.
    """

    def accumulate_variant(self, allele_response):
        """
        Accumulates the information about the AlleleResponseAccumulation object variant
        for visibility level 10 which changes the coarse phenotype.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        super(VariantAccumulator10, self).accumulate_variant(allele_response)
        for p in Phenotype.objects.filter(case=allele_response.variant.case):
            allele_response.coarse_phenotype = allele_response.coarse_phenotype.union(
                p.get_coarse_phenotype()
            )


class VariantAccumulator5(VariantAccumulator15):
    """
    Accumulator class for visibility level 5: accumulates information about existence,
    frequency count, sample count, variantCount>10, allele count and phenotype.
    """

    def accumulate_variant(self, allele_response):
        """
        Accumulates the information about the AlleleResponseAccumulation object variant
        for visibility level 5 which changes the phenotype.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        super(VariantAccumulator5, self).accumulate_variant(allele_response)
        for p in Phenotype.objects.filter(case=allele_response.variant.case):
            allele_response.phenotype = allele_response.phenotype.union({p.phenotype})


class VariantAccumulator0(VariantAccumulator5):
    """
    Accumulator class for visibility level 0: accumulates information about existence,
    frequency count, sample count, variantCount>10, allele count, phenotype and case index.
    """

    def accumulate_variant(self, allele_response):
        """
        Accumulates the information about the AlleleResponseAccumulation object variant
        for visibility level 0 which changes the case index.

        :param allele_response: An AlleleResponseAccumulation object.
        """
        super(VariantAccumulator0, self).accumulate_variant(allele_response)
        # get case identifier
        allele_response.case_indices.append(allele_response.variant.case.index)
