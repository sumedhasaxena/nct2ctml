import unittest
from pprint import pprint

from utils.oncotree import (
    _get_level_columns,
    _parse_level_value,
    _read_oncotree_rows,
    get_all_oncotree_data,
    get_l1_l2_oncotree_data,
)


class TestOncotree(unittest.TestCase):

    def test_get_level_columns(self):
        fieldnames = ["level_3", "level_1", "metamaintype", "level_2"]
        self.assertEqual(_get_level_columns(fieldnames), ["level_1", "level_2", "level_3"])

    def test_parse_level_value(self):
        self.assertEqual(_parse_level_value("Breast (BREAST)"), "Breast")

    def test_read_oncotree_rows(self):
        rows, level_columns = _read_oncotree_rows()
        self.assertGreater(len(rows), 0)
        self.assertEqual(level_columns[0], "level_1")
        self.assertEqual(len(level_columns), 6)

    def test_get_all_oncotree_data(self):
        level_1_list, mapping_l1_all = get_all_oncotree_data()
        self.assertIn("Breast", level_1_list)
        self.assertGreater(len(mapping_l1_all["Breast"]), 0)

    def test_get_l1_l2_oncotree_data(self):
        level_1_list, mapping_l1_l2 = get_l1_l2_oncotree_data()
        pprint(sorted(level_1_list))
        pprint({k: sorted(v) for k, v in mapping_l1_l2.items()})
        self.assertIn("Breast", level_1_list)
        self.assertGreater(len(mapping_l1_l2["Breast"]), 0)
        self.assertIn("Diffuse Glioma", mapping_l1_l2["CNS/Brain"])


if __name__ == "__main__":
    unittest.main()
