import requests
import urllib
import json

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAK1tcwEAAAAAIB4QgUopSxqOrKTGsF2DOXFzMEg%3DSUmGqxQCsqOPUBAMx4rqqlGtq72VdooeUWqsY5FTCJbj6anxVG"
headers = {"Authorization": f"Bearer {BEARER_TOKEN} "}
query = urllib.parse.quote("モバレ")
url = f'https://api.twitter.com/2/tweets/search/recent?query={query}&max_results={100} -is:retweet'
response = requests.get(url, headers=headers)
json_response = response.json()
print(json.dumps(json_response, indent=2, ensure_ascii=False))