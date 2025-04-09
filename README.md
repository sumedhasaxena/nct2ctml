This application pulls clinical trials from https://clinicaltrials.gov/, converts them to a CTML compliant schema to be used by Matchminer platform, and saves the converted trial files (JSON & YAML) locally.

**Source**:
https://clinicaltrials.gov/data-api/api#extapi

**Target**:
CTML compliant documents: Clinical Trial Markup Language (CTML) is a human readable markup language that allows users to structure clinical trial details including clinical and genomic eligibility. (https://matchminer.org/#ctml)

------------


**Usage:**
> python main.py [pull all | pull {nct_id} | map all | map {nct_id}]

###### python main.py pull all

Pulls all NCT trial studies based on locally defined filters. Saves the files locally in JSON format.

###### python main.py pull {nct_id}

Pulls the specified NCT trial study. Saves the file locally in JSON format.

###### python main.py map all

Assumes that the NCT trial studies are already pulled and stored locally in JSON format. It reads the files and converts them to CTML compliant schema, ready-to-be uploaded to matchminer platform.

###### python main.py map {nct_id}

Assumes that the mentioned NCT trial study is already pulled and stored locally in JSON format. It reads the file and converts it to CTML compliant schema, ready-to-be uploaded to matchminer platform.
