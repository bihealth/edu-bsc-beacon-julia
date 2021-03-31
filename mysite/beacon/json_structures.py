class AlleleRequest:

    def __init__(self, chromosome, start, end, reference, alternative, release):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.reference = reference
        self.alternative = alternative
        self.release = release

    def create_dict(self):
        allele_request_dict = {"referenceName": self.chromosome,
                               "start": self.start,
                               "end": self.end,
                               "referenceBases": self.reference,
                               "alternateBases": self.alternative,
                               "assemblyId": self.release
                               }

        return allele_request_dict


class AlleleResponse:

    def __init__(self, exists, variant_count_greater_ten, variant_count, coarse_phenotype, phenotype, case_name):
        self.exists = exists
        self.variant_count_greater_ten = variant_count_greater_ten
        self.variant_count = variant_count
        self.coarse_phenotype = coarse_phenotype
        self.phenotype = phenotype
        self.case_name = case_name

    def create_dict_25(self):
        allele_response_dict = {"exists": self.exists,
                                "error": None
                                }
        return allele_response_dict

    def create_dict_20(self):
        allele_response_dict = {"exists": self.exists,
                                "alleleCount>10": self.variant_count_greater_ten,
                                "error": None
                                }
        return allele_response_dict

    def create_dict_15(self):
        allele_response_dict = {"exists": self.exists,
                                "alleleCount": self.variant_count,
                                "error": None
                                }
        return allele_response_dict

    def create_dict_10(self):
        allele_response_dict = {"exists": self.exists,
                                "alleleCount": self.variant_count,
                                "coarsePhenotype": self.coarse_phenotype,
                                "error": None
                                }
        return allele_response_dict

    def create_dict_5(self):
        allele_response_dict = {"exists": self.exists,
                                "alleleCount": self.variant_count,
                                "phenotype": self.phenotype,
                                "error": None
                                }
        return allele_response_dict

    def create_dict_0(self):
        allele_response_dict = {"exists": self.exists,
                                "alleleCount": self.variant_count,
                                "phenotype": self.phenotype,
                                "caseName": self.case_name,
                                "error": None
                                }
        return allele_response_dict
