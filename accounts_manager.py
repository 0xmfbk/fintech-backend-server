import requests
from fastapi import FastAPI, HTTPException, Query
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

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
    
    def _get_supabase_client(self) -> Client:
        """Get Supabase client instance"""
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials are not set.")
        return create_client(self.supabase_url, self.supabase_key)
    
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


# Test functionality when run as script
if __name__ == "__main__":
    # Sample customer IDs for testing
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
    
    print("Testing Accounts Manager...")
    for cid in sample_customer_ids:
        print(f"\nProcessing customer_id={cid}")
        try:
            result = accounts_processor.process_customer_accounts(cid)
            print("Customer Summary:")
            print(f"  customerId: {result['customerId']}")
            print(f"  accounts_count: {result['accounts_count']}")
            print(f"  total_balance: {result['total_balance']}")
            print(f"  total_credit: {result['total_credit']}")
            print(f"  total_debit: {result['total_debit']}")
            print("  accounts:")
            for acc in result['accounts']:
                print(f"    - bank_name: {acc['bank_name']}")
                print(f"      account_status: {acc['account_status']}")
                print(f"      balance_amount: {acc['balance_amount']}")
                print(f"      balance_position: {acc['balance_position']}")
                print(f"      account_currency: {acc['account_currency']}")
                print(f"      account_address: {acc['account_address']}")
                print(f"      account_id: {acc['account_id']}")
        except Exception as e:
            print(f"Error processing accounts for {cid}: {e}") 
