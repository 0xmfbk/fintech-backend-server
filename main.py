from fastapi import FastAPI, HTTPException, Query
from accounts_fetcher import AccountsFetcher
from supabase_client import get_supabase
from typing import List, Dict, Any

app = FastAPI()

@app.post("/fetch-accounts")
def fetch_accounts(customer_id: str = Query(..., description="Customer ID to fetch accounts for")):
    # 1. Fetch data from external API
    fetcher = AccountsFetcher(
        url="https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/Accounts/v0.4.3/accounts",
        customerId=customer_id
    )
    try:
        data = fetcher.get_full_account()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch accounts: {str(e)}")

    # 2. Extract all required fields for each account
    accounts = []
    total_credit = 0.0
    total_debit = 0.0
    customer_id_value = customer_id
    for acc in data.get("data", []):
        name_obj = acc.get("institutionBasicInfo", {}).get("name", {})
        bank_name = name_obj.get("tradeName", {}).get("enName") or name_obj.get("enName")
        account_status = acc.get("accountStatus")
        balance_amount = acc.get("availableBalance", {}).get("amount", 0.0)
        balance_position = acc.get("availableBalance", {}).get("balancePosition")
        account_currency = acc.get("accountCurrency")
        account_address = acc.get("mainRoute", {}).get("address")
        account_id = acc.get("accountId")
        customer_id_value = acc.get("customerId", customer_id_value)
        accounts.append({
            "bank_name": bank_name,
            "account_status": account_status,
            "balance_amount": balance_amount,
            "balance_position": balance_position,
            "account_currency": account_currency,
            "account_address": account_address,
            "account_id": account_id,
            "customer_id": customer_id_value
        })
        # Calculate total credit and debit separately
        if balance_position == "credit":
            total_credit += balance_amount
        elif balance_position == "debit":
            total_debit += balance_amount

    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found or missing required fields.")

    # Calculate net balance (credit - debit)
    total_balance = total_credit - total_debit

    # 3. Store all accounts in Supabase (bulk upsert)
    supabase = get_supabase()
    try:
        result = supabase.table("Accounts").upsert(
            accounts,
            on_conflict="account_id,customer_id"
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upsert into Supabase: {str(e)}")

    # 4. Return summary
    return {
        "customerId": customer_id_value,
        "accounts_count": len(accounts),
        "accounts": accounts,
        "total_balance": total_balance
    } 