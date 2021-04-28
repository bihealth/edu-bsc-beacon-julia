from django.test import TestCase
from ..queries import CaseQueryVariant
from .factories import (
        VariantFactory,
        PhenotypeFactory
    )


class TestQueryVariant(TestCase):
    def setUp(self):
        self.variant = VariantFactory()
        self.case_query_variant = CaseQueryVariant()
        PhenotypeFactory(case=self.variant.case)

    def test_create(self):
        self.assertEqual(self.case_query_variant.exists, False)
        self.assertEqual(self.case_query_variant.allele_count_greater_ten, False)
        self.assertEqual(self.case_query_variant.allele_count, 0)
        self.assertEqual(self.case_query_variant.internal_allele_count, 0)
        self.assertListEqual(self.case_query_variant.coarse_phenotypes, [])
        self.assertListEqual(self.case_query_variant.phenotypes, [])
        self.assertListEqual(self.case_query_variant.case_indices, [])

    def test_make_query_20(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_20(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.allele_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.allele_count, 0)
            self.assertEqual(self.case_query_variant.internal_allele_count, i)
            self.assertListEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertListEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_20(self.variant)
        self.assertEqual(self.case_query_variant.allele_count_greater_ten, True)

    def test_make_query_15(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_15(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.allele_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.allele_count, i)
            self.assertEqual(self.case_query_variant.internal_allele_count, 0)
            self.assertListEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertListEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_15(self.variant)
        self.assertEqual(self.case_query_variant.allele_count_greater_ten, True)

    def test_make_query_10(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_10(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.allele_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.allele_count, i)
            self.assertEqual(self.case_query_variant.internal_allele_count, 0)
            self.assertNotEqual(self.case_query_variant.coarse_phenotypes, [])
            for p in self.case_query_variant.coarse_phenotypes:
                self.assertEqual(PhenotypeFactory(phenotype=p).get_coarse_phenotype(), p)
            self.assertListEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_10(self.variant)
        self.assertEqual(self.case_query_variant.allele_count_greater_ten, True)

    def test_make_query_5(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_5(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.allele_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.allele_count, i)
            self.assertEqual(self.case_query_variant.internal_allele_count, 0)
            self.assertListEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertNotEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [])
        self.case_query_variant.make_query_5(self.variant)
        self.assertEqual(self.case_query_variant.allele_count_greater_ten, True)

    def test_make_query_0(self):
        for i in range(1, 11):
            self.case_query_variant.make_query_0(self.variant)
            self.assertEqual(self.case_query_variant.exists, False)
            self.assertEqual(self.case_query_variant.allele_count_greater_ten, False)
            self.assertEqual(self.case_query_variant.allele_count, i)
            self.assertEqual(self.case_query_variant.internal_allele_count, 0)
            self.assertListEqual(self.case_query_variant.coarse_phenotypes, [])
            self.assertNotEqual(self.case_query_variant.phenotypes, [])
            self.assertListEqual(self.case_query_variant.case_indices, [self.variant.case.index]*i)
        self.case_query_variant.make_query_0(self.variant)
        self.assertEqual(self.case_query_variant.allele_count_greater_ten, True)
