from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

SUPABASE_URL = "https://eruinevvxatdagfqlzwn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVydWluZXZ2eGF0ZGFnZnFsenduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI3ODUwMjIsImV4cCI6MjA2ODM2MTAyMn0.FTw_VbIEGVIAW3Huhz8ghtJzPV3tNcvWXPuNVxCu-eE"

def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials are not set.")
    return create_client(SUPABASE_URL, SUPABASE_KEY) 