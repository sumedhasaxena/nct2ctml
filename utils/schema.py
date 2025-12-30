    # json_schema = {
    # "type": "object",
    # "properties": {
    #     "hugo_symbol": {"type": "string"},
    #     "variant_category": {"type": "string"}
    # },
    # "required": ["hugo_symbol", "variant_category"]}

#     json_schema = {
#     "type": "object",
#     "properties": {
#         "genomic": {
#             "type": "object",
#             "properties": {
#                 "hugo_symbol": {"type": "string"},
#                 "variant_category": {
#                     "type": "string",
#                     "enum": ["Mutation", "Copy Number Variation", "Structural Variation", "Any Variation", "!Mutation", "!Copy Number Variation", "!Structural Variation"]
#                 },
#                 "protein_change": {"type": "string"},
#                 "cnv_call": {
#                     "type": "string",
#                     "enum": ["High level amplification", "Homozygous deletion", "Gain", "Heterozygous deletion"]
#                 }
#             },
#             "required": ["hugo_symbol", "variant_category"]
#             # Remove additionalProperties: false if causing issues
#         }
#     },
#     "required": ["genomic"]
# }

# trial_genomic_json_schema = {
#             "type": "object",
#             "properties": {
#                 "genomic": {
#                     "type": "object",
#                     "properties": {
#                         "hugo_symbol": {
#                             "type": "string"
#                         },
#                         "variant_category": {
#                             "type": "string",
#                             "enum": [
#                                 "Mutation",
#                                 "Copy Number Variation",
#                                 "Structural Variation",
#                                 "Any Variation",
#                                 "!Mutation",
#                                 "!Copy Number Variation",
#                                 "!Structural Variation"
#                             ],
#                             "description": "Variant category with '!' prefix for exclusions"
#                         },
#                         "protein_change": {
#                             "type": "string",
#                             "description": "Only for 'Mutation' variant_category. Format: Starting with 'p.', e.g., p.R177H, p.L858R, p.N435Kfs*4"
#                         },
#                         "cnv_call": {
#                             "type": "string",
#                             "enum": [
#                                 "High level amplification",
#                                 "Homozygous deletion",
#                                 "Gain",
#                                 "Heterozygous deletion"
#                             ],
#                             "description": "Only for 'Copy Number Variation' variant_category"
#                         }
#                     },
#                     "required": [
#                         "hugo_symbol",
#                         "variant_category"
#                     ],
#                     "additionalProperties": False,
#                 }
#             },
#             "required": [
#                 "genomic"
#             ]
#         }

trial_genomic_json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Genomic Eligibility Schema",
    "type": "object",
    "oneOf": [
        {
            "type": "object",
            "properties": {
                "genomic": {
                    "type": "object",
                    "properties": {
                        "hugo_symbol": {"type": "string"},
                        "variant_category": {
                            "type": "string",
                            "enum": ["Mutation", "Copy Number Variation", "Structural Variation", "Any Variation", "!Mutation", "!Copy Number Variation", "!Structural Variation"],
                            "description": "Variant category with '!' prefix for exclusions"
                        },
                        "protein_change": {"type": "string","description": "Only for 'Mutation' variant_category. Format: Starting with 'p.', e.g., p.R177H, p.L858R, p.N435Kfs*4"},
                        "cnv_call": {
                            "type": "string",
                            "enum": ["High level amplification", "Homozygous deletion", "Gain", "Heterozygous deletion"],
                            "description": "To be used only if variant_category = 'Copy Number Variation'"
                        }
                    },
                    "required": ["hugo_symbol", "variant_category"],
                    "additionalProperties": False
                }
            },
            "required": ["genomic"],
            "additionalProperties": False
        },
        {
            "type": "object",
            "properties": {
                "or": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "genomic": {
                                "type": "object",
                                "properties": {
                                    "hugo_symbol": {"type": "string"},
                                    "variant_category": {"type": "string"},
                                    "protein_change": {"type": "string"},
                                    "cnv_call": {"type": "string"}
                                },
                                "required": ["hugo_symbol", "variant_category"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["genomic"],
                        "additionalProperties": False
                    },
                    "minItems": 1
                }
            },
            "required": ["or"],
            "additionalProperties": False
        },
        {
            "type": "object",
            "properties": {
                "and": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "genomic": {
                                "type": "object",
                                "properties": {
                                    "hugo_symbol": {"type": "string"},
                                    "variant_category": {"type": "string"},
                                    "protein_change": {"type": "string"},
                                    "cnv_call": {"type": "string"}
                                },
                                "required": ["hugo_symbol", "variant_category"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["genomic"],
                        "additionalProperties": False
                    },
                    "minItems": 1
                }
            },
            "required": ["and"],
            "additionalProperties": False
        }
    ]
}


    # json_schema = {
    #         "type": "object",
    #         "properties": {
    #             "genomic": {
    #                 "type": "object",
    #                 "properties": {
    #                     "hugo_symbol": {
    #                         "type": "string"
    #                     },
    #                     "variant_category": {
    #                         "type": "string",
    #                         "enum": [
    #                             "Mutation",
    #                             "Copy Number Variation",
    #                             "Structural Variation",
    #                             "Any Variation",
    #                             "!Mutation",
    #                             "!Copy Number Variation",
    #                             "!Structural Variation"
    #                         ],
    #                         "description": "Variant category with '!' prefix for exclusions"
    #                     },
    #                     "protein_change": {
    #                         "type": "string",
    #                         "pattern": "^p\\.[A-Z][a-z]{2}\\d+[A-Za-z*]",
    #                         "description": "Only for 'Mutation' variant_category"
    #                     },
    #                     "cnv_call": {
    #                         "type": "string",
    #                         "enum": [
    #                             "High level amplification",
    #                             "Homozygous deletion",
    #                             "Gain",
    #                             "Heterozygous deletion"
    #                         ],
    #                         "description": "Only for 'Copy Number Variation' variant_category"
    #                     }
    #                 },
    #                 "required": [
    #                     "hugo_symbol",
    #                     "variant_category"
    #                 ],
    #                 "additionalProperties": False,
    #             }
    #         },
    #         "required": [
    #             "genomic"
    #         ]
    #     }