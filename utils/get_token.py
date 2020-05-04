import requests
import json
from utils.globals import url

class get:
    @staticmethod
    def get_api(user, passw):
        try:
            r = requests.post(url, data=json.dumps({'email':user, "password":passw}),allow_redirects=False,verify=False,
            headers={'Content-Type': 'application/json'}).json()
            return r

        except Exception as e:
            return False
