-- Supabase Schema for Accounts Table
-- This table stores account information fetched from external API

-- Create the Accounts table with all required fields
CREATE TABLE IF NOT EXISTS "Accounts" (
    -- Primary key
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Account identification
    "account_id" TEXT NOT NULL,
    "customer_id" TEXT NOT NULL,
    
    -- Bank information
    "bank_name" TEXT,
    
    -- Account status and type
    "account_status" TEXT,
    
    -- Financial information
    "balance_amount" DECIMAL(15,2),
    "balance_position" TEXT,
    "account_currency" TEXT,
    
    -- Account routing
    "account_address" TEXT,
    
    -- Metadata
    "created_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create unique constraint to prevent duplicate accounts
-- Each account_id should be unique per customer
CREATE UNIQUE INDEX IF NOT EXISTS "accounts_account_customer_unique" 
ON "Accounts" ("account_id", "customer_id");

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS "accounts_customer_id_idx" ON "Accounts" ("customer_id");
CREATE INDEX IF NOT EXISTS "accounts_account_status_idx" ON "Accounts" ("account_status");
CREATE INDEX IF NOT EXISTS "accounts_bank_name_idx" ON "Accounts" ("bank_name");
CREATE INDEX IF NOT EXISTS "accounts_created_at_idx" ON "Accounts" ("created_at");

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_accounts_updated_at 
    BEFORE UPDATE ON "Accounts" 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for better security
ALTER TABLE "Accounts" ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (you can customize this based on your needs)
CREATE POLICY "Allow all operations on Accounts" ON "Accounts"
    FOR ALL USING (true);

-- Optional: Create a view for customer summary
CREATE OR REPLACE VIEW "customer_accounts_summary" AS
SELECT 
    customer_id,
    COUNT(*) as accounts_count,
    SUM(balance_amount) as total_balance,
    STRING_AGG(DISTINCT account_status, ', ') as account_statuses,
    STRING_AGG(DISTINCT bank_name, ', ') as banks
FROM "Accounts"
GROUP BY customer_id;

-- Optional: Create a function to get customer summary
CREATE OR REPLACE FUNCTION get_customer_summary(customer_id_param TEXT)
RETURNS TABLE (
    customer_id TEXT,
    accounts_count BIGINT,
    total_balance DECIMAL(15,2),
    account_statuses TEXT,
    banks TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.customer_id,
        COUNT(*) as accounts_count,
        SUM(a.balance_amount) as total_balance,
        STRING_AGG(DISTINCT a.account_status, ', ') as account_statuses,
        STRING_AGG(DISTINCT a.bank_name, ', ') as banks
    FROM "Accounts" a
    WHERE a.customer_id = customer_id_param
    GROUP BY a.customer_id;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE "Accounts" IS 'Stores account information fetched from external API';
COMMENT ON COLUMN "Accounts"."account_id" IS 'Unique account identifier from external system';
COMMENT ON COLUMN "Accounts"."customer_id" IS 'Customer identifier from external system';
COMMENT ON COLUMN "Accounts"."balance_amount" IS 'Current account balance';
COMMENT ON COLUMN "Accounts"."balance_position" IS 'credit or debit position';
COMMENT ON COLUMN "Accounts"."account_address" IS 'IBAN or account routing address'; 