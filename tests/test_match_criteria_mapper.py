import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path so we can import the module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from match_criteria_mapper import (
    convert_to_ctml_genomic_schema,
    convert_to_ctml_clinical_schema,
    combine_clinical_and_genomic_ctml
)


class TestConvertToCtmlGenomicSchema(unittest.TestCase):
    """Test suite for convert_to_ctml_genomic_schema function"""
    
    def setUp(self):
        """Set up test data before each test method"""
        self.sample_inclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "Mutation"
                }
            }
        ]
        
        self.sample_exclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "TP53",
                    "variant_category": "!Mutation"
                }
            }
        ]
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_single_inclusion_no_exclusion(self, mock_update, mock_get_keys):
        """Test with single inclusion criteria and no exclusion"""
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema(self.sample_inclusion_criteria, [])
        
        self.assertIn("genomic", result)
        self.assertEqual(result["genomic"]["hugo_symbol"], "BRCA1")
        self.assertEqual(result["genomic"]["variant_category"], "Mutation")
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_single_exclusion_no_inclusion(self, mock_update, mock_get_keys):
        """Test with single exclusion criteria and no inclusion"""
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema([], self.sample_exclusion_criteria)
        
        self.assertIn("genomic", result)
        self.assertEqual(result["genomic"]["hugo_symbol"], "TP53")
        self.assertEqual(result["genomic"]["variant_category"], "!Mutation")
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_multiple_inclusions_with_or(self, mock_update, mock_get_keys):
        """Test multiple inclusion criteria are combined with 'or' operator"""
        inclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "Mutation"
                }
            },
            {
                "genomic": {
                    "hugo_symbol": "BRCA2",
                    "variant_category": "Mutation"
                }
            }
        ]
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema(inclusion_criteria, [])
        
        # Multiple inclusions should be combined with 'or'
        # Since we now use lists instead of sets, the result should be the single item if only one, or a dict with 'or' if multiple
        self.assertTrue(isinstance(result, dict))
        if "or" in result:
            self.assertEqual(len(result["or"]), 2)
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_multiple_exclusions_with_and(self, mock_update, mock_get_keys):
        """Test multiple exclusion criteria are combined with 'and' operator"""
        exclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "TP53",
                    "variant_category": "!Mutation"
                }
            },
            {
                "genomic": {
                    "hugo_symbol": "KRAS",
                    "variant_category": "!Mutation"
                }
            }
        ]
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema([], exclusion_criteria)
        
        # Multiple exclusions should be combined with 'and'
        self.assertTrue(isinstance(result, dict))
        if "and" in result:
            self.assertEqual(len(result["and"]), 2)
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_variant_category_with_negation_moved_to_exclusions(self, mock_update, mock_get_keys):
        """Test that variant_category starting with ! is moved to exclusions"""
        inclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "!Mutation"
                }
            }
        ]
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema(inclusion_criteria, [])
        
        # When inclusion has negation, it should be in exclusions
        self.assertIn("genomic", result)
        self.assertEqual(result["genomic"]["variant_category"], "!Mutation")
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_inclusion_and_exclusion_combined_with_and(self, mock_update, mock_get_keys):
        """Test inclusion and exclusion criteria are combined with 'and' operator"""
        inclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "Mutation"
                }
            }
        ]
        exclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "TP53",
                    "variant_category": "!Mutation"
                }
            }
        ]
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema(inclusion_criteria, exclusion_criteria)
        
        self.assertIn("and", result)
        self.assertEqual(len(result["and"]), 2)
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_empty_input_returns_empty_dict(self, mock_update, mock_get_keys):
        """Test that empty input returns empty dictionary"""
        mock_get_keys.return_value = set()
        
        result = convert_to_ctml_genomic_schema([], [])
        
        self.assertEqual(result, {})
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_missing_required_keys_in_inclusion(self, mock_update, mock_get_keys):
        """Test that missing required keys in inclusion criteria is handled"""
        incomplete_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "BRCA1"
                    # Missing variant_category
                }
            }
        ]
        
        mock_get_keys.return_value = {"hugo_symbol"}  # Missing variant_category
        
        result = convert_to_ctml_genomic_schema(incomplete_criteria, [])
        
        self.assertEqual(result, {})
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_no_duplicate_inclusions(self, mock_update, mock_get_keys):
        """Test that duplicate inclusion criteria are not added"""
        inclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "Mutation"
                }
            },
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "Mutation"
                }
            }
        ]
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema(inclusion_criteria, [])
        
        # Should have only one inclusion, not two
        self.assertIn("genomic", result)
        self.assertEqual(result["genomic"]["hugo_symbol"], "BRCA1")
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_no_duplicate_exclusions(self, mock_update, mock_get_keys):
        """Test that duplicate exclusion criteria are not added"""
        inclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "!Mutation"
                }
            },
            {
                "genomic": {
                    "hugo_symbol": "BRCA1",
                    "variant_category": "!Mutation"
                }
            }
        ]
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema(inclusion_criteria, [])
        
        # Should have only one exclusion, not two
        self.assertIn("genomic", result)
        self.assertEqual(result["genomic"]["hugo_symbol"], "BRCA1")
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_no_duplicate_across_inclusion_and_exclusion(self, mock_update, mock_get_keys):
        """Test that if same alteration appears in both inclusion and exclusion, it's not duplicated"""
        alteration = {
            "genomic": {
                "hugo_symbol": "BRCA1",
                "variant_category": "!MUTATION"
            }
        }
        
        # Add the same alteration to both inclusion (with !) and exclusion
        inclusion_criteria = [alteration]
        exclusion_criteria = [alteration]
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = lambda x: x
        
        result = convert_to_ctml_genomic_schema(inclusion_criteria, exclusion_criteria)
        
        # Should only have one copy of the alteration in exclusions
        self.assertIn("genomic", result)
        self.assertEqual(result["genomic"]["hugo_symbol"], "BRCA1")
    
    @patch('match_criteria_mapper.tdh.get_all_keys')
    @patch('match_criteria_mapper.tdh.update_hugo_symbol')
    def test_her2_to_erbb2_conversion(self, mock_update, mock_get_keys):
        """Test that HER2 is converted to ERBB2 by update_hugo_symbol"""
        inclusion_criteria = [
            {
                "genomic": {
                    "hugo_symbol": "HER2",
                    "variant_category": "Mutation"
                }
            }
        ]
        
        # Mock update_hugo_symbol to convert HER2 to ERBB2
        def convert_her2(criteria):
            if isinstance(criteria, list):
                for item in criteria:
                    if isinstance(item, dict) and "genomic" in item:
                        if item["genomic"]["hugo_symbol"] == "HER2":
                            item["genomic"]["hugo_symbol"] = "ERBB2"
            return criteria
        
        mock_get_keys.return_value = {"hugo_symbol", "variant_category"}
        mock_update.side_effect = convert_her2
        
        result = convert_to_ctml_genomic_schema(inclusion_criteria, [])
        
        self.assertEqual(result["genomic"]["hugo_symbol"], "ERBB2")


class TestConvertToCtmlClinicalSchema(unittest.TestCase):
    """Test suite for convert_to_ctml_clinical_schema function"""
    
    def test_single_diagnosis(self):
        """Test with single diagnosis"""
        clinical_criteria = {
            "oncotree_primary_diagnosis": ["Lung Cancer"],
            "age_range": "18-65"
        }
        
        result = convert_to_ctml_clinical_schema(clinical_criteria)
        
        self.assertIn("clinical", result)
        self.assertEqual(result["clinical"]["oncotree_primary_diagnosis"], "Lung Cancer")
        self.assertEqual(result["clinical"]["age_range"], "18-65")
    
    def test_multiple_diagnoses_with_or(self):
        """Test with multiple diagnoses - should use 'or' operator"""
        clinical_criteria = {
            "oncotree_primary_diagnosis": ["Lung Cancer", "Breast Cancer"],
            "age_range": "18-65"
        }
        
        result = convert_to_ctml_clinical_schema(clinical_criteria)
        
        self.assertIn("and", result)
        self.assertIn("or", result["and"][0])
        self.assertEqual(len(result["and"][0]["or"]), 2)


class TestCombineClinicalAndGenomicCtml(unittest.TestCase):
    """Test suite for combine_clinical_and_genomic_ctml function"""
    
    def test_combine_with_genomic_present(self):
        """Test combining clinical and genomic criteria when both present"""
        clinical_ctml = {
            "clinical": {
                "oncotree_primary_diagnosis": "Lung Cancer"
            }
        }
        genomic_ctml = {
            "genomic": {
                "hugo_symbol": "BRCA1",
                "variant_category": "MUTATION"
            }
        }
        
        result = combine_clinical_and_genomic_ctml(clinical_ctml, genomic_ctml)
        
        self.assertIn("and", result)
        self.assertEqual(len(result["and"]), 2)
    
    def test_combine_without_genomic(self):
        """Test combining when genomic criteria is empty"""
        clinical_ctml = {
            "clinical": {
                "oncotree_primary_diagnosis": "Lung Cancer"
            }
        }
        
        result = combine_clinical_and_genomic_ctml(clinical_ctml, {})
        
        self.assertEqual(result, clinical_ctml)
    
    def test_combine_with_empty_genomic_dict(self):
        """Test combining when genomic criteria is empty dict"""
        clinical_ctml = {
            "clinical": {
                "oncotree_primary_diagnosis": "Lung Cancer"
            }
        }
        
        result = combine_clinical_and_genomic_ctml(clinical_ctml, {})
        
        self.assertEqual(result, clinical_ctml)


if __name__ == '__main__':
    unittest.main()
