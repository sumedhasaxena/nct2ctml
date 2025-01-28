import requests
import urllib.parse

API_BASE_URL = "https://clinicaltrials.gov/api/v2/"

def get_nct_data(nct_id:str):
    NCT_STUDY_ENDPOINT = "studies/{0}".format(nct_id)
    endpoint_url = urllib.parse.urljoin(API_BASE_URL, NCT_STUDY_ENDPOINT)
    response = requests.get(endpoint_url)
    response.raise_for_status()
    return response.json()
    

