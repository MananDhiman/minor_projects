import time
import requests

# creds
DREMIO_URL = "http://localhost:9047"
USERNAME = "manan"
PASSWORD = "PqK9DF3c"

headers = {"Content-Type": "application/json"}

# get temp token, TODO check how to use PAT token w/o temp token
# TODO check how use /api/v3
login_payload = {"userName": USERNAME, "password": PASSWORD}
login_response = requests.post(
    f"{DREMIO_URL}/apiv2/login", json=login_payload, headers=headers
)
login_response.raise_for_status()

token = f"_dremio{login_response.json()['token']}"
auth_headers = {"Content-Type": "application/json", "Authorization": token}

### TODO test pat token prodecure, will not need to get temp 'token', also may skip /api/v2
# PAT_TOKEN = "your_personal_access_token_here"

# auth_headers = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {PAT_TOKEN}",
# }

table = 'Samples."samples.dremio.com"."NYC-weather.csv"'

sql_query = {"sql": f"SELECT * FROM {table} LIMIT 1"}
# sql_query = {"sql": f"SELECT 5 * 5"}

# post query
query_response = requests.post(
    f"{DREMIO_URL}/api/v3/sql", json=sql_query, headers=auth_headers
)
query_response.raise_for_status()

# get job_id
job_id = query_response.json()["id"]

# keep checking using job id until job complete
seconds = 0
while True:
    job_status_resp = requests.get(
        f"{DREMIO_URL}/api/v3/job/{job_id}", headers=auth_headers
    )
    job_status = job_status_resp.json()["jobState"]

    # TODO configure databricks job success or fail, will auto send mail
    if job_status == "COMPLETED":
        break
    elif job_status in ["FAILED", "CANCELED"]:
        raise Exception(f"Query failed with status: {job_status}")

    print(f"Please wait, checking job status...   {seconds} seconds have passed")
    time.sleep(10)
    seconds += 10

# get result when job done
results_response = requests.get(
    f"{DREMIO_URL}/api/v3/job/{job_id}/results", headers=auth_headers
)

# can skip print if mail sent
print(results_response.json())


### TODO Check infor audit log ingestion
