class AlleleRequest:

    def __init__(self, chromosome, start, end, reference, alternative):
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.reference = reference
        self.alternative = alternative

    def create_dict(self):
        allele_request_dict["alleleRequest"] = {"referenceName": self.chromosome,
                                                "start": self.start,
                                                "end": self.end,
                                                "referenceBases": self.reference,
                                                "alternateBases": self.alternative
                                                }
        return allele_request_dict


class AlleleResponse:

    def __init__(self, exists, variant_count_greater_ten, variant_count,  coarse_phenotype, phenotype):
        self.exists = exists
        self.variant_count = variant_count
        self.coarse_phenotype = coarse_phenotype
        self.phenotype = phenotype

    def create_dict(self):
        allele_response_dict["datasetAlleleResponses"] = {"exists": self.exists,
                                                          "variantCount>10": self.variant_count_greater_ten,
                                                          "variantCount": self.variant_count,
                                                          "coarsePhenotype": self.coarse_phenotype,
                                                          "phenotype": self.phenotype
                                                          }
        return allele_response_dict
