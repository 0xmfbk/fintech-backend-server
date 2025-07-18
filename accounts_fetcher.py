import requests

class AccountsFetcher:
    def __init__(self, url, customerId):
        self.url = url
        self.customerId = customerId

    def get_full_account(self):
        url = self.url
        querystring = {"skip": "0", "limit": "10", "sort": "desc"}
        headers = {
            "x-jws-signature": "1",
            "x-auth-date": "1",
            "x-idempotency-key": "1",
            "Authorization": "1",
            "x-customer-user-agent": "1",
            "x-financial-id": "1",
            "x-customer-ip-address": "1",
            "x-interactions-id": "1",
            "x-customer-id": str(self.customerId)
        }
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    sample_customer_ids = [
        "IND_CUST_001",
        "IND_CUST_017",
        "IND_CUST_009",
        "IND_CUST_015",
        "CORP_CUST_001",
        "CORP_CUST_008",
        "BUS_CUST_001",
        "BUS_CUST_005"
    ]
    url = "https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/Accounts/v0.4.3/accounts"
    for cid in sample_customer_ids:
        print(f"\nFetching accounts for customer_id={cid}")
        fetcher = AccountsFetcher(url, cid)
        try:
            data = fetcher.get_full_account()
            accounts = []
            total_credit = 0.0
            total_debit = 0.0
            customer_id_value = cid
            for acc in data.get("data", []):
                name_obj = acc.get("institutionBasicInfo", {}).get("name", {})
                bank_name = name_obj.get("tradeName", {}).get("enName") or name_obj.get("enName")
                account_status = acc.get("accountStatus")
                balance_amount = acc.get("availableBalance", {}).get("balanceAmount", 0.0)
                balance_position = acc.get("availableBalance", {}).get("balancePosition")
                account_currency = acc.get("accountCurrency")
                account_address = acc.get("mainRoute", {}).get("address")
                account_id = acc.get("accountId")
                accounts.append({
                    "bank_name": bank_name,
                    "account_status": account_status,
                    "balance_amount": balance_amount,
                    "balance_position": balance_position,
                    "account_currency": account_currency,
                    "account_address": account_address,
                    "account_id": account_id
                })
                # Calculate total credit and debit separately
                if balance_position == "credit":
                    total_credit += balance_amount
                elif balance_position == "debit":
                    total_debit += balance_amount
            # Calculate net balance (credit - debit)
            total_balance = total_credit - total_debit
            print("Customer Summary:")
            print(f"  customerId: {customer_id_value}")
            print(f"  accounts_count: {len(accounts)}")
            print(f"  total_balance: {total_balance}")
            print("  accounts:")
            for acc in accounts:
                print(f"    - bank_name: {acc['bank_name']}")
                print(f"      account_status: {acc['account_status']}")
                print(f"      balance_amount: {acc['balance_amount']}")
                print(f"      balance_position: {acc['balance_position']}")
                print(f"      account_currency: {acc['account_currency']}")
                print(f"      account_address: {acc['account_address']}")
                print(f"      account_id: {acc['account_id']}")
        except Exception as e:
            print(f"Error fetching accounts for {cid}: {e}") 