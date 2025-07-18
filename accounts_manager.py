import requests
from fastapi import FastAPI, HTTPException, Query, status, Body, Path
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from paymentPlan import paymentplan, get_payment_plan_blocks, initiate_payment
from offer import get_offers

# Load environment variables
load_dotenv()

class SupabaseClient:
    """Simple Supabase client using requests"""
    def __init__(self, url, key):
        self.url = url
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    def table(self, table_name):
        return SupabaseTable(self.url, table_name, self.headers)

class SupabaseTable:
    def __init__(self, base_url, table_name, headers):
        self.base_url = base_url
        self.table_name = table_name
        self.headers = headers
        self.table_url = f"{base_url}/rest/v1/{table_name}"
    
    def upsert(self, data, on_conflict=None):
        return SupabaseQuery(self.table_url, self.headers, data, on_conflict)

class SupabaseQuery:
    def __init__(self, url, headers, data, on_conflict):
        self.url = url
        self.headers = headers
        self.data = data
        self.on_conflict = on_conflict
    
    def execute(self):
        try:
            if self.on_conflict:
                self.headers["Prefer"] = f"resolution=merge-duplicates"
            
            response = requests.post(
                self.url,
                headers=self.headers,
                json=self.data
            )
            response.raise_for_status()
            
            return SupabaseResult(data=self.data)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Supabase request failed: {str(e)}")

class SupabaseResult:
    def __init__(self, data=None):
        self.data = data or []

class AccountsFetcher:
    """Class to fetch account data from external API"""
    
    def __init__(self, url: str, customerId: str):
        self.url = url
        self.customerId = customerId

    def get_full_account(self) -> Dict:
        """Fetch full account data from external API"""
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


class SupabaseManager:
    """Class to manage Supabase operations"""
    
    def __init__(self):
        self.supabase_url = "https://eruinevvxatdagfqlzwn.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVydWluZXZ2eGF0ZGFnZnFsenduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3ODUwMjIsImV4cCI6MjA2ODM2MTAyMn0.FTw_VbIEGVIAW3Huhz8ghtJzPV3tNcvWXPuNVxCu-eE"
        self.client = self._get_supabase_client()
    
    def _get_supabase_client(self):
        """Get Supabase client instance"""
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials are not set.")
        return SupabaseClient(self.supabase_url, self.supabase_key)
    
    def upsert_accounts(self, accounts: List[Dict]) -> List[Dict]:
        """Upsert accounts into Supabase"""
        try:
            result = self.client.table("Accounts").upsert(
                accounts,
                on_conflict="account_id,customer_id"
            ).execute()
            return result.data
        except Exception as e:
            raise Exception(f"Failed to upsert into Supabase: {str(e)}")


class AccountsProcessor:
    """Class to process and extract account information"""
    
    def __init__(self):
        self.supabase_manager = SupabaseManager()
    
    def extract_account_data(self, raw_data: Dict) -> Dict:
        """Extract and process account data from raw API response"""
        accounts = []
        total_credit = 0.0
        total_debit = 0.0
        customer_id_value = None
        
        for acc in raw_data.get("data", []):
            # Extract bank name with fallback logic
            name_obj = acc.get("institutionBasicInfo", {}).get("name", {})
            bank_name = name_obj.get("tradeName", {}).get("enName") or name_obj.get("enName")
            
            # Extract other account information
            account_status = acc.get("accountStatus")
            balance_amount = float(acc.get("availableBalance", {}).get("balanceAmount", 0.0))
            balance_position = acc.get("availableBalance", {}).get("balancePosition")
            account_currency = acc.get("accountCurrency")
            account_address = acc.get("mainRoute", {}).get("address")
            account_id = acc.get("accountId")
            customer_id_value = acc.get("customerId", customer_id_value)
            
            # Create account object
            account_obj = {
                "bank_name": bank_name,
                "account_status": account_status,
                "balance_amount": balance_amount,
                "balance_position": balance_position,
                "account_currency": account_currency,
                "account_address": account_address,
                "account_id": account_id,
                "customer_id": customer_id_value
            }
            accounts.append(account_obj)
            
            # Calculate credit and debit totals
            if balance_position == "credit":
                total_credit += balance_amount
            elif balance_position == "debit":
                total_debit += balance_amount
        
        # Calculate net balance
        total_balance = total_credit - total_debit
        
        # Debug: Print balance information
        print(f"Debug - Customer: {customer_id_value}")
        print(f"Debug - Total Credit: {total_credit}")
        print(f"Debug - Total Debit: {total_debit}")
        print(f"Debug - Net Balance: {total_balance}")
        for acc in accounts:
            print(f"Debug - Account {acc['account_id']}: {acc['balance_amount']} ({acc['balance_position']})")
        
        return {
            "accounts": accounts,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "total_balance": total_balance,
            "customer_id": customer_id_value
        }
    
    def process_customer_accounts(self, customer_id: str) -> Dict:
        """Process accounts for a specific customer"""
        # Fetch data from external API
        fetcher = AccountsFetcher(
            url="https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/Accounts/v0.4.3/accounts",
            customerId=customer_id
        )
        
        try:
            raw_data = fetcher.get_full_account()
        except Exception as e:
            raise Exception(f"Failed to fetch accounts: {str(e)}")
        
        # Extract and process account data
        processed_data = self.extract_account_data(raw_data)
        
        if not processed_data["accounts"]:
            raise Exception("No accounts found or missing required fields.")
        
        # Store in Supabase
        try:
            self.supabase_manager.upsert_accounts(processed_data["accounts"])
        except Exception as e:
            raise Exception(f"Failed to store accounts: {str(e)}")
        
        # Return summary
        return {
            "customerId": processed_data["customer_id"],
            "accounts_count": len(processed_data["accounts"]),
            "accounts": processed_data["accounts"],
            "total_balance": processed_data["total_balance"],
            "total_credit": processed_data["total_credit"],
            "total_debit": processed_data["total_debit"]
        }


# FastAPI Application
app = FastAPI(title="Accounts Management API", description="API for fetching and managing customer accounts")

# Global processor instance
accounts_processor = AccountsProcessor()


@app.post("/fetch-accounts")
def fetch_accounts(customer_id: str = Query(..., description="Customer ID to fetch accounts for")):
    """Fetch and store customer accounts"""
    try:
        result = accounts_processor.process_customer_accounts(customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts")
def get_accounts(customer_id: str = Query(..., description="Customer ID to get accounts for")):
    """Get customer accounts directly from external API without storing"""
    try:
        # Fetch data from external API
        fetcher = AccountsFetcher(
            url="https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/Accounts/v0.4.3/accounts",
            customerId=customer_id
        )
        
        raw_data = fetcher.get_full_account()
        
        # Extract and process account data
        processed_data = accounts_processor.extract_account_data(raw_data)
        
        if not processed_data["accounts"]:
            raise HTTPException(status_code=404, detail="No accounts found for this customer.")
        
        # Return summary without storing in database
        return {
            "customerId": processed_data["customer_id"],
            "accounts_count": len(processed_data["accounts"]),
            "accounts": processed_data["accounts"],
            "total_balance": processed_data["total_balance"],
            "total_credit": processed_data["total_credit"],
            "total_debit": processed_data["total_debit"],
            "source": "external_api",
            "stored_in_database": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get accounts: {str(e)}")


@app.get("/accounts/{customer_id}")
def get_accounts_by_path(customer_id: str):
    """Get customer accounts using path parameter"""
    try:
        # Fetch data from external API
        fetcher = AccountsFetcher(
            url="https://jpcjofsdev.apigw-az-eu.webmethods.io/gateway/Accounts/v0.4.3/accounts",
            customerId=customer_id
        )
        
        raw_data = fetcher.get_full_account()
        
        # Extract and process account data
        processed_data = accounts_processor.extract_account_data(raw_data)
        
        if not processed_data["accounts"]:
            raise HTTPException(status_code=404, detail="No accounts found for this customer.")
        
        # Return summary without storing in database
        return {
            "customerId": processed_data["customer_id"],
            "accounts_count": len(processed_data["accounts"]),
            "accounts": processed_data["accounts"],
            "total_balance": processed_data["total_balance"],
            "total_credit": processed_data["total_credit"],
            "total_debit": processed_data["total_debit"],
            "source": "external_api",
            "stored_in_database": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get accounts: {str(e)}")


@app.get("/customer-exists/{customer_id}")
def customer_exists(customer_id: str):
    """Check if a customer exists in Supabase Accounts table by customer_id."""
    supabase_url = "https://eruinevvxatdagfqlzwn.supabase.co/rest/v1/Accounts"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVydWluZXZ2eGF0ZGFnZnFsenduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3ODUwMjIsImV4cCI6MjA2ODM2MTAyMn0.FTw_VbIEGVIAW3Huhz8ghtJzPV3tNcvWXPuNVxCu-eE"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    params = {"customer_id": f"eq.{customer_id}", "select": "customer_id", "limit": 1}
    try:
        response = requests.get(supabase_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        exists = len(data) > 0
        return {"exists": exists, "customer_id": customer_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check customer: {str(e)}") 


@app.get("/accounts/{account_id}/transactions")
def get_transactions_for_account(account_id: str):
    """
    Get all transactions for a given account from Supabase.
    """
    supabase_manager = SupabaseManager()
    try:
        url = f"{supabase_manager.supabase_url}/rest/v1/Transactions"
        headers = {
            "apikey": supabase_manager.supabase_key,
            "Authorization": f"Bearer {supabase_manager.supabase_key}",
            "Content-Type": "application/json"
        }
        params = {
            "account_id": f"eq.{account_id}"
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        transactions = response.json()
        return {"account_id": account_id, "transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transactions: {str(e)}") 

@app.post("/payment-plan")
def api_payment_plan(
    amount: float = Query(..., description="Amount for the payment plan"),
    x_customer_id: str = Query(..., description="Customer ID (e.g., IND_CUST_001)")
):
    return paymentplan(amount, x_customer_id)

@app.post("/payment-plan/blocks")
def api_get_payment_plan_blocks_post(
    payment_plan_id: str = Body(..., description="Payment Plan ID"),
    x_customer_id: str = Body(..., description="Customer ID (e.g., IND_CUST_001)")
):
    return get_payment_plan_blocks(payment_plan_id, x_customer_id)

@app.post("/payment-initiate")
def api_initiate_payment(
    payment_plan_id: str = Query(..., description="Payment Plan ID"),
    block_id: str = Query(..., description="Block ID"),
    amount: float = Query(..., description="Amount for the payment"),
    x_customer_id: str = Query(..., description="Customer ID (e.g., IND_CUST_001)")
):
    # Mocked response for testing
    return {
        "status": "success",
        "message": "Payment initiated successfully (mocked)",
        "payment_plan_id": payment_plan_id,
        "block_id": block_id,
        "amount": amount,
        "x_customer_id": x_customer_id,
        "transaction_id": "MOCKED_TXN_12345"
    }

@app.get("/offers")
def api_get_offers():
    return get_offers()
