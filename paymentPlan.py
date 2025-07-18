import requests
import json



def paymentplan(ammount, x_customer_id):
    url = "https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/RFC%20-%20Payment%20Initiation%20Services%20%28PIS%29/v0.4.3/paymentPlan"
    payload = {
        "accounts": [
            {
                "accountAgentParty": "cdtrAgt",
                "accountType": "cdtrAcct",
                "mainRoute": {
                    "address": "IND_CUST_001",
                    "schema": "qMybXYjHb"
                }
            }
        ],
        "agents": [
            {
                "agent": {
                    "additionalInfo": [
                        {"key": "OaUFAGx",
                        "value": "A"}
                    ],
                    "address": {
                        "addresslines": [],
                        "city": "gWqeQamMHNJ",
                        "countryInfo": {
                            "countryCode": "JO",
                            "countryName": "pWj"
                        },
                        "postcode": "CneUkNcesBr",
                        "state": "OhiQgqyAVbUa"
                    },
                    "agentIdentification": {
                        "address": "IND_CUST_001",
                        "schema": "DJWo"
                    },
                    "enName": "ktIFvEjyWPeC"
                },
                "agentType": "cdtrAgt"
            }
        ],
        "endToEnd": "bphscaOo",
        "involvedParties": [
            {
                "involvedParty": {
                    "additionalInfo": [
                        {
                            "key": "VKVEOoSJNoP",
                            "value": "KlPvFhfAfS"
                        }
                    ],
                    "address": {
                        "addresslines": [],
                        "city": "YbJSHjoRwM",
                        "countryInfo": {
                            "countryCode": "JO",
                            "countryName": "msLElEQpr"
                        },
                        "postcode": "wAtBS",
                        "state": "uDKHhddmXUgS"
                    },
                    "enName": "QftUXRmQjnpGDe"
                },
                "involvedPartyType": "cdtr"
            }
        ],
        "paymentDetails": {
            "expirationDate": "2025-07-18",
            "frequency": "pqcA",
            "recurringPaymentAmount": {
                "amount": ammount,
                "currency": "JOR"
            },
            "rmtInf": "deQgulPTWmxC",
            "setAmount": {
                "amount": ammount,
                "currency": "JOR"
            },
            "setNumberOfPayments": 1467098562
        },
        "paymentPlanAuthPurposeCode": "ICv"
    }
    headers = {
        "x-financial-id": "1",
        "x-customer-user-agent": "1",
        "x-customer-id": f"{x_customer_id}",
        "x-interactions-id": "1",
        "Authorization": "1",
        "x-customer-ip-address": "1",
        "x-jws-signature": "1",
        "x-auth-date": "1",
        "x-idempotency-key": "1",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response_text = response.text
    data = json.loads(response_text)
    #payment_plan_id = data['paymentPlanId']
    return data

def get_payment_plan_blocks(payment_plan_id, x_customer_id):
    url = f"https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/RFC%20-%20Payment%20Initiation%20Services%20%28PIS%29/v0.4.3/paymentPlan/{payment_plan_id}/blocks"

    headers = {
        "x-idempotency-key": "1",
        "x-customer-id": f"{x_customer_id}",
        "Authorization": "1",
        "x-customer-user-agent": "1",
        "x-auth-date": "1",
        "x-customer-ip-address": "1",
        "x-interactions-id": "1",
        "x-jws-signature": "1",
        "x-financial-id": "1"
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching payment plan blocks: {response.status_code} - {response.text}")
    if len(response.text) > 20 :
        response_block_text = response.text
        #print(response_block_text)
    else :
        response_block_text = """
    [  {
        "blockId": "BLOCK-000001",
        "blockPaymentAmount": {
        "amount": "10.00",
        "currency": "JOD"
        },
        "totalResult": "PASS",
        "endToEnd": "1234DK",
        "UUID": "cct6",
        "timestamp": "2006-09-15T10:30:00Z",
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJlbmRUb0VuZCI6ImVuZFRvRW5kMSIsIlVVSUQiOiI5NmU2MTliNC00NWQxLTRkMDEtOTM3ZC1kZmZkNzE0NGJjZWYiLCJ0aW1lU3RhbXAiOiIyMDI0LTA1LTI3VDA4OjU2OjAzLjg5NFoifQ.V9dAxAC_pdqBwcuw3uwL5gFGdaTe6xNZD3cUD8UzbneDXRL-uSy-6XVOH-pfiCWXI38S4lm67M_SFRSjZSF2KhsPFr1ejtQH5zkJcpM-cRif9JaS7U7oLCEUSmFZe5MtPxUZbap_bLqG66o-ZMFd_psigmVWxJI-ctVg36MS4nd7AqwEhvkw2Zb3X8IztQ-rUam_Tnb3l2KA5SVa9fo7myyX4VYcVTi9jgif3setTW1w0DdVFGVo1Kj0c71vlTNNYITja_p4h6LX5G2haeyVDc4mh4jErrsXwAP7RiD-n6dKDRdYpJjtX7BAlvPHUuI8dRnnbPPMlwADsTFpFifeHQ"
    }]
    """
    data_block = json.loads(response_block_text)
    #blockId = data_block[0]['blockId']
    #print(blockId)
    return data_block

def initiate_payment(payment_plan_id, blockId, ammount, x_customer_id):
    url = "https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/RFC%20-%20Payment%20Initiation%20Services%20%28PIS%29/v0.4.3/PIS/initiation"

    payload = {
        "groupHeader": {
            "batchBooking": "ortnDSVNBr",
            "batchPurpose": "kLtAdesqiNxcgv",
            "creationDateTime": "2025-07-18",
            "numberOfTrx": "OTvhSBY",
            "paymentMethod": "oS",
            "totalTrxAmount": {
                "amount": ammount,
                "currency": "JOD"
            }
        },
        "instructionsInfo": [
            {
                "accounts": [
                    {
                        "accountAgentParty": "InitgPty",
                        "accountType": "cdtrAcct",
                        "mainRoute": {
                            "address": "mJBGMcsSrr",
                            "schema": "FuUKMmnIcAOHe"
                        }
                    }
                ],
                "agents": [
                    {
                        "agent": {
                            "additionalInfo": [
                                {
                                    "key": "EoRMXdNlE",
                                    "value": "XWghUo"
                                }
                            ],
                            "address": {
                                "addresslines": [],
                                "city": "lO",
                                "countryInfo": {
                                    "countryCode": "JO",
                                    "countryName": "vuCwu"
                                },
                                "postcode": "lCrfWOxKg",
                                "state": "cgjPPWYkQei"
                            },
                            "agentIdentification": {
                                "address": "vEGbDTQaKa",
                                "schema": "MpjupA"
                            },
                            "enName": "tMOiNijfc"
                        },
                        "agentType": "cdtrAgt"
                    }
                ],
                "categoryPurpose": "lKKlVheQqSE",
                "clearingChannel": "RTGS",
                "identifications": {
                    "SOSPId": "g",
                    "blockId": blockId,
                    "endToEnd": "hoJFVwFmNEsaAt",
                    "fxQuoteId": "vbnBkpdbBVQuvE",
                    "paymentPlanId": payment_plan_id,
                    "quoteId": "KhfhVTAKPwF",
                    "trxId": "IOoiGjhlTf"
                },
                "involvedParties": [
                    {
                        "involvedParty": {
                            "additionalInfo": [
                                {
                                    "key": "tPoxqBfcvyFj",
                                    "value": "YRkKikfloUTYDb"
                                }
                            ],
                            "address": {
                                "addresslines": [],
                                "city": "NwTWoXQlv",
                                "countryInfo": {
                                    "countryCode": "JO",
                                    "countryName": "BwmLHaL"
                                },
                                "postcode": "UQM",
                                "state": "igskxkkOJjS"
                            },
                            "enName": "o"
                        },
                        "involvedPartyType": "ultmtCdtr"
                    }
                ],
                "localInstrument": "sOjUxWT",
                "regulatoryReporting": [],
                "remittanceInformation": {
                    "unstructured": []
                },
                "serviceLevel": "vlsIEaFDJIhJM",
                "supplementaryData": [
                    {
                        "key": "neSwHkYkvl",
                        "value": "AScqVdWASna"
                    }
                ],
                "trxAmount": {
                    "amount": ammount,
                    "currency": "JOD"
                },
                "trxPresDateTime": "2025-07-18"
            }
        ]
    }
    headers = {
        "x-financial-id": "1",
        "x-customer-user-agent": "1",
        "Authorization": "1",
        "x-auth-date": "1",
        "x-jws-signature": "1",
        "x-idempotency-key": "1",
        "x-customer-id": f"{x_customer_id}",
        "x-interactions-id": "1",
        "x-customer-ip-address": "1",
        "content-type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response

#Test the functions
if __name__ == "__main__":
    
    ammount = 1000  # Example amount
    x_customer_id = "IND_CUST_001"
    paymentplan_data = paymentplan(ammount, x_customer_id)
    payment_plan_id = paymentplan_data['paymentPlanId']
    print(f"Payment Plan ID: {payment_plan_id}")
    
    blocks = get_payment_plan_blocks(payment_plan_id, x_customer_id)
    blocks_id = blocks[0]['blockId']
    print(f"Block ID: {blocks_id}")
    
    response = initiate_payment(payment_plan_id, blocks_id, ammount, x_customer_id)
    print(f"Initiate Payment Response: {response.text}")
