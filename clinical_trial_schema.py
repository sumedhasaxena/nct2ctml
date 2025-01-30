import yaml

def get_trial_schema():
    return {
  'nct_id': '',
  'age': 'Adults',
  'cancer_center_accrual_goal_upper': 0,
  'data_table4': 'Interventional',
  'drug_list': {
    'drug': []
  },
  'long_title': '',
  'management_group_list': {
    'management_group': [
      {
        'is_primary': 'Y',
        'management_group_name': ''
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
        'step_code': '1',
        'step_type': 'Registration',
        'step_internal_id': 1111,
        'arm': [
          {
            'arm_code': 'Arm A',
            'arm_internal_id': 1111,
            'arm_description': '',
            'arm_suspended': 'N',
            'dose_level': [
              {
                'level_code': '1',
                'level_description': '',
                'level_internal_id': 1,
                'level_suspended': 'N'
              }
            ]
          },
          {
            'arm_code': 'Arm B',
            'arm_internal_id': 2222,
            'arm_description': '',
            'arm_suspended': 'N',
            'dose_level': [
              {
                'level_code': '1',
                'level_description': '',
                'level_internal_id': 1,
                'level_suspended': 'N'
              }
            ]
          }
        ],
        'match': [
          {
            'and': [
              {
                'clinical': {
                  'oncotree_primary_diagnosis': '',
                  'disease_status': [
                    '',
                    ''
                  ]
                }
              },
              {
                'genomic': {
                  'hugo_symbol': '',
                  'variant_category': ''
                }
              }
            ]
          }
        ]
      }
    ]
  }
}