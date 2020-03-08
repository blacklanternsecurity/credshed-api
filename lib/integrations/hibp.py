import json
import requests

breach_list = json.loads(requests.get('https://haveibeenpwned.com/api/v3/breaches'))