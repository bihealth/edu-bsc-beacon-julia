from django.test import TestCase
from ..queries import CaseQueryVariant
from .factories import (
        VariantFactory,
        PhenotypeFactory,
        CaseFactory
    )


class TestQueryVariant(TestCase):
    def setUp(self):
        self.case = CaseFactory()
        self.variant = VariantFactory(case=self.case)
        self.case_query_variant = CaseQueryVariant()
        self.phenotype = PhenotypeFactory(case=self.variant.case, phenotype="HP:0001049")

    def test_create(self):
        self.assertEqual(self.case_query_variant.exists, False)
        self.assertEqual(self.case_query_variant.variant_count_greater_ten, False)
        self.assertEqual(self.case_query_variant.variant_count, 0)
        self.assertEqual(self.case_query_variant.internal_variant_count, 0)
        self.assertEqual(self.case_query_variant.frequency, 0)
        self.assertEqual(self.case_query_variant.coarse_phenotypes, [])
        self.assertEqual(self.case_query_variant.phenotypes, [])
        self.assertListEqual(self.case_query_variant.case_indices, [])

    def test_make_query_25(self):
        self.case_query_variant.make_query_25(self.variant)
        self.assertEqual(self.case_query_variant.exists, False)
        self.assertEqual(self.case_query_variant.sample_count, 1)
        self.assertEqual(self.case_query_variant.variant_count_greater_ten, False)
        self.assertEqual(self.case_query_variant.variant_count, 0)
        self.assertEqual(self.case_query_variant.internal_variant_count, 0)
        self.assertEqual(self.case_query_variant.frequency, 0)
        self.assertEqual(self.case_query_variant.coarse_phenotypes, [])
        self.assertEqual(self.case_query_variant.phenotypes, [])
        self.assertListEqual(self.case_query_variant.case_indices, [])

    def test_make_query_20(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_20(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.variant_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.variant_count, 0)
            self.assertEqual(self.case_query_variant.internal_variant_count, i)
            self.assertEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_20(self.variant)
        self.assertEqual(self.case_query_variant.variant_count_greater_ten, True)
        self.assertEqual(self.case_query_variant.frequency, 0)

    def test_make_query_15(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_15(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.variant_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.variant_count, i)
            self.assertEqual(self.case_query_variant.internal_variant_count, 0)
            self.assertEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_15(self.variant)
        self.assertEqual(self.case_query_variant.variant_count_greater_ten, True)
        self.assertEqual(self.case_query_variant.frequency, 0)

    def test_make_query_10(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_10(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.variant_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.variant_count, i)
            self.assertEqual(self.case_query_variant.internal_variant_count, 0)
            self.assertNotEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_10(self.variant)
        self.assertEqual(self.case_query_variant.variant_count_greater_ten, True)
        self.assertEqual(self.case_query_variant.frequency, 0)

    def test_make_query_5(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_5(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.variant_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.variant_count, i)
            self.assertEqual(self.case_query_variant.internal_variant_count, 0)
            self.assertEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertNotEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_5(self.variant)
        self.assertEqual(self.case_query_variant.variant_count_greater_ten, True)
        self.assertEqual(self.case_query_variant.frequency, 0)

    def test_make_query_0(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_0(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.variant_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.variant_count, i)
            self.assertEqual(self.case_query_variant.internal_variant_count, 0)
            self.assertEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertNotEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [self.variant.case.index]*i)
        self.case_query_variant.make_query_0(self.variant)
        self.assertEqual(self.case_query_variant.variant_count_greater_ten, True)
        self.assertEqual(self.case_query_variant.frequency, 0)
