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

    def __init__(self, exists, allele_count_greater_ten, allele_count, coarse_phenotype, phenotype, case_indices):
        self.exists = exists
        self.allele_count_greater_ten = allele_count_greater_ten
        self.allele_count = allele_count
        self.coarse_phenotype = coarse_phenotype
        self.phenotype = phenotype
        self.case_indices = case_indices

    def create_dict(self):
        allele_response_dict = {"exists": self.exists,
                                "alleleCount>10": self.allele_count_greater_ten,
                                "alleleCount": self.allele_count,
                                "coarsePhenotype": self.coarse_phenotype,
                                "phenotype": self.phenotype,
                                "caseName": self.case_indices,
                                "error": None
                                }
        return allele_response_dict
