from django.test import TestCase
from .factories import VariantFactory, PhenotypeFactory, CaseFactory
from ..variant_accumulation import (
    VariantAccumulator0,
    VariantAccumulator5,
    VariantAccumulator10,
    VariantAccumulator15,
    VariantAccumulator20,
    VariantAccumulator20Internal,
    VariantAccumulator25,
)
from ..beacon_schemas import AlleleResponseAccumulation


class TestVariantAccumulator(TestCase):
    """Test case for QueryVariant methods"""

    #: Set up parameters needed for queries
    def setUp(self):
        self.case = CaseFactory()
        self.variant = VariantFactory(case=self.case, chromosome=1)
        self.phenotype = PhenotypeFactory(
            case=self.variant.case, phenotype="HP:0001049"
        )

    #: Test class VariantAccumulator25
    def test_variant_accumulator_25(self):
        allele_response = AlleleResponseAccumulation()
        allele_response.variant = self.variant
        variant_accumulation = VariantAccumulator25()
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.exists, True)
        self.assertEqual(allele_response.sample_count, 1)
        self.assertEqual(allele_response.variant_count_greater_ten, False)
        self.assertEqual(allele_response.variant_count, 0)
        self.assertEqual(allele_response.internal_variant_count, 0)
        self.assertEqual(allele_response.frequency_count, 2)
        self.assertEqual(allele_response.frequency, 0)
        self.assertEqual(allele_response.coarse_phenotype, set())
        self.assertEqual(allele_response.phenotype, set())
        self.assertListEqual(allele_response.case_indices, [])

    #: Test class VariantAccumulator20
    def test_variant_accumulator_20(self):
        allele_response = AlleleResponseAccumulation()
        allele_response.variant = self.variant
        variant_accumulation = VariantAccumulator20()
        for i in range(1, 11):
            variant_accumulation.accumulate(allele_response)
            self.assertEqual(allele_response.exists, True)
            self.assertEqual(allele_response.variant_count_greater_ten, False)
            self.assertEqual(allele_response.variant_count, 0)
            self.assertEqual(allele_response.internal_variant_count, i)
            self.assertEqual(allele_response.coarse_phenotype, set())
            self.assertEqual(allele_response.phenotype, set())
            self.assertListEqual(allele_response.case_indices, [])
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.variant_count_greater_ten, True)
        self.assertEqual(allele_response.frequency, 0)

    #: Test class VariantAccumulator20Internal
    def test_variant_accumulator_20_internal(self):
        allele_response = AlleleResponseAccumulation()
        allele_response.variant = self.variant
        variant_accumulation = VariantAccumulator20Internal()
        variant_accumulation_20 = VariantAccumulator20()
        variant_accumulation_15 = VariantAccumulator15()
        self.assertEqual(allele_response.variant_count_greater_ten, False)
        for i in range(1, 6):
            variant_accumulation_20.accumulate(allele_response)
            variant_accumulation_15.accumulate(allele_response)
        variant_accumulation_15.accumulate(allele_response)
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.exists, True)
        self.assertEqual(allele_response.variant_count, 6)
        self.assertEqual(allele_response.internal_variant_count, 5)
        self.assertEqual(allele_response.variant_count_greater_ten, True)
        self.assertEqual(allele_response.coarse_phenotype, set())
        self.assertEqual(allele_response.phenotype, set())
        self.assertListEqual(allele_response.case_indices, [])
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.frequency, 0)

    #: Test class VariantAccumulator15
    def test_variant_accumulator_15(self):
        allele_response = AlleleResponseAccumulation()
        allele_response.variant = self.variant
        variant_accumulation = VariantAccumulator15()
        for i in range(1, 11):
            variant_accumulation.accumulate(allele_response)
            self.assertEqual(allele_response.exists, True)
            self.assertEqual(allele_response.variant_count_greater_ten, False)
            self.assertEqual(allele_response.variant_count, i)
            self.assertEqual(allele_response.internal_variant_count, 0)
            self.assertEqual(allele_response.coarse_phenotype, set())
            self.assertEqual(allele_response.phenotype, set())
            self.assertListEqual(allele_response.case_indices, [])
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.variant_count_greater_ten, True)
        self.assertEqual(allele_response.frequency, 0)

    #: Test class VariantAccumulator10
    def test_variant_accumulator_10(self):
        allele_response = AlleleResponseAccumulation()
        allele_response.variant = self.variant
        variant_accumulation = VariantAccumulator10()
        for i in range(1, 11):
            variant_accumulation.accumulate(allele_response)
            self.assertEqual(allele_response.exists, True)
            self.assertEqual(allele_response.variant_count_greater_ten, False)
            self.assertEqual(allele_response.variant_count, i)
            self.assertEqual(allele_response.internal_variant_count, 0)
            self.assertNotEqual(allele_response.coarse_phenotype, set())
            self.assertEqual(allele_response.phenotype, set())
            self.assertListEqual(allele_response.case_indices, [])
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.variant_count_greater_ten, True)
        self.assertEqual(allele_response.frequency, 0)

    #: Test class VariantAccumulator5
    def test_variant_accumulator_5(self):
        allele_response = AlleleResponseAccumulation()
        allele_response.variant = self.variant
        variant_accumulation = VariantAccumulator5()
        for i in range(1, 11):
            variant_accumulation.accumulate(allele_response)
            self.assertEqual(allele_response.exists, True)
            self.assertEqual(allele_response.variant_count_greater_ten, False)
            self.assertEqual(allele_response.variant_count, i)
            self.assertEqual(allele_response.internal_variant_count, 0)
            self.assertEqual(allele_response.coarse_phenotype, set())
            self.assertNotEqual(allele_response.phenotype, set())
            self.assertListEqual(allele_response.case_indices, [])
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.variant_count_greater_ten, True)
        self.assertEqual(allele_response.frequency, 0)

    #: Test class VariantAccumulator0
    def test_variant_accumulator_0(self):
        allele_response = AlleleResponseAccumulation()
        allele_response.variant = self.variant
        variant_accumulation = VariantAccumulator0()
        for i in range(1, 11):
            variant_accumulation.accumulate(allele_response)
            self.assertEqual(allele_response.exists, True)
            self.assertEqual(allele_response.variant_count_greater_ten, False)
            self.assertEqual(allele_response.variant_count, i)
            self.assertEqual(allele_response.internal_variant_count, 0)
            self.assertEqual(allele_response.coarse_phenotype, set())
            self.assertNotEqual(allele_response.phenotype, set())
            self.assertListEqual(
                allele_response.case_indices, [self.variant.case.index] * i
            )
        variant_accumulation.accumulate(allele_response)
        self.assertEqual(allele_response.variant_count_greater_ten, True)
        self.assertEqual(allele_response.frequency, 0)
