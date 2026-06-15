import sys
import os

sys.path.append(os.path.abspath('../'))

import csv
from collections import defaultdict
import config


def _get_level_columns(fieldnames):
    return sorted(
        (f for f in fieldnames if f.startswith('level_')),
        key=lambda name: int(name.split('_')[1]),
    )


def _parse_level_value(value):
    return value.split('(')[0].strip()


def _read_oncotree_rows():
    with open(config.ONCOTREE_TXT_FILE_PATH) as f:
        reader = csv.DictReader(f, delimiter='\t')
        level_columns = _get_level_columns(reader.fieldnames)
        rows = list(reader)
    return rows, level_columns


def get_all_oncotree_data():
    rows, level_columns = _read_oncotree_rows()

    level_1_list = set()
    mapping_l1_all = defaultdict(set)

    for row in rows:
        level_1 = _parse_level_value(row[level_columns[0]])
        level_1_list.add(level_1)
        mapping_l1_all[level_1].update(
            _parse_level_value(row[col]) for col in level_columns[1:]
        )

    for s in mapping_l1_all.values():
        if '' in s:
            s.remove('')
    return level_1_list, mapping_l1_all


def get_l1_l2_oncotree_data():
    print(config.ONCOTREE_TXT_FILE_PATH)
    rows, level_columns = _read_oncotree_rows()

    level_1_list = set()
    mapping_11_l2 = defaultdict(set)

    for row in rows:
        level_1 = _parse_level_value(row[level_columns[0]])
        level_1_list.add(level_1)
        if len(level_columns) > 1:
            level_2 = _parse_level_value(row[level_columns[1]])
            mapping_11_l2[level_1].update({level_2})

    for s in mapping_11_l2.values():
        if '' in s:
            s.remove('')

    return level_1_list, mapping_11_l2
