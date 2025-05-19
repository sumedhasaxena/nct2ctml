import unittest
from patient_data.get_gene_from_seq_id import get_gene_info

class TestGetGeneInfoFromNCBI(unittest.TestCase):
    def setUp(self):
        self.ref_seq ="NM_016169.3"

    def test_get_gene_info(self):
        gene_info = get_gene_info(self.ref_seq)
        self.assertTrue('(SUFU)' in gene_info)

if __name__ == "__main__":
    unittest.main()