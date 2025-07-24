# nct2ctml

The **nct2ctml** repository is a specialized ETL (Extract, Transform, Load) application for clinical trial data. It provides a CLI interface for pulling and mapping trial data from [ClinicalTrials.gov](https://clinicaltrials.gov/data-api/api#extapi) to the Clinical Trial Markup Language ([CTML](https://matchminer.gitbook.io/matchminer/deployment/ctml-and-trial-curation)) schema format.

---

## Features
- Pulls trial data from ClinicalTrials.gov
- Converts trial data to CTML schema format
- Saves converted trial files locally (YAML and JSON)
- Uses Oncotree and gene reference data for mapping
- CLI interface for automation and scripting

> **Manual Curation:**
> For manual creation or editing of CTML files, please refer to the guide at [`doc/trial_creation_guide.md`](doc/trial_creation_guide.md).
> Plans for new workflow: https://miro.com/app/board/uXjVJcuSvUY=/?share_link_id=429445659556
---

For detailed information about the system architecture and component relationships, see:
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sumedhasaxena/nct2ctml)

---

## Quick Start

### Prerequisites
- Python 3.12 recommended

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/sumedhasaxena/nct2ctml.git
   cd nct2ctml
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the CLI from the project root:

```bash
python main.py [-h] {pull,map} ...
```

### Commands

#### Pull NCT study data
- Pull all studies:
  ```bash
  python main.py pull --all
  ```
- Pull a specific study:
  ```bash
  python main.py pull --nct_id NCT_ID
  ```
- Pull existing studies (from local list):
  ```bash
  python main.py pull --existing
  ```

#### Map NCT IDs to CTML
- Map all NCT files:
  ```bash
  python main.py map --all
  ```
- Map a specific NCT ID:
  ```bash
  python main.py map --nct_id NCT_ID
  ```

---

## Running Tests

- **Run all tests:**
  ```bash
  python -m unittest discover -s tests -v
  ```
- **Run a specific test:**
  ```bash
  python -m unittest tests.test_your_module.TestGetGeneInfo.test_get_gene_info -v
  ```

---

## Resources
- [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api#extapi)
- [MatchMiner CTML](https://matchminer.gitbook.io/matchminer/deployment/ctml-and-trial-curation)
- [Oncotree (oncotree_2021_11_02)](https://oncotree.mskcc.org/?version=oncotree_2021_11_02&field=NAME)
- [COSMIC Cancer Gene Census](https://cancer.sanger.ac.uk/census)
- [Manual CTML Curation Guide](doc/trial_creation_guide.md)
