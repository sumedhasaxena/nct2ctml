'''
This script contains defines the clinical trial schema as requied by Matchminer app
'''

def get_ctml_schema():
    return {
  'nct_id': '',
  'age': 'Adults',
  'cancer_center_accrual_goal_upper': 0,
  'curated_on': '',
  'data_table4': 'Interventional',
  'drug_list': {
    'drug': []
  },
  'long_title': '',
  'last_updated': '',
  'management_group_list': {
    'management_group': [
      {
        'is_primary': 'Y',
        'management_group_name': 'Group1'
      }
    ]
  },
  'oncology_group_list': {
    'oncology_group': [
      {
        'group_name': 'Group1',
        'is_primary': 'N'
      }
    ]
  },
  'phase': '',
  'principal_investigator': '',
  'principal_investigator_institution': '',
  'program_area_list': {
    'program_area': [
      {
        'is_primary': 'Y',
        'program_area_name': 'Program1'
      }
    ]
  },
  'protocol_id': 0,
  'protocol_ids': [], # list of local protocol IDs
  'protocol_no': '',
  'protocol_target_accrual': 0,
  'protocol_type': 'INTERVENTIONAL',
  'prior_treatment_requirements': [],
  'short_title': '',
  'site_list': {
    'site': []
  },
  'sponsor_list': {
    'sponsor': []
  },
  'staff_list': {
    'protocol_staff': []
  },
  'status': 'open to accrual',
  'summary': '',
  'treatment_list': {
    'step': [
      {
        'step_internal_id': 111,
        'step_code': '1',
        'step_type': 'Registration',
        'arm': [],
        'match': []
      }
    ]
  }
}