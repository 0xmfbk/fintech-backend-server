import requests
import json

def get_offers():
    url = "https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/Offers/v0.4.3/institution/offers"

    querystring = {"sort":"desc","limit":"10","skip":"0"}

    headers = {
        "x-idempotency-key": "1",
        "x-interactions-id": "1",
        "Authorization": "1",
        "x-financial-id": "1",
        "x-jws-signature": "1"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_text = response.text
    response_json = json.loads(response_text)
    return response_json
