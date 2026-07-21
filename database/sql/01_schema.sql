-- =====================================================================
-- SalesGenie AI — PostgreSQL Database Schema
-- Module: Database & DevOps Engineering
-- Description: Core schema for Lead Management, Lead Intelligence,
--              Outreach, Conversation Intelligence, Lead Scoring,
--              and CRM Sync Logging.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. Extensions & Setup
-- ---------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- for gen_random_uuid() if ever needed
CREATE EXTENSION IF NOT EXISTS "citext";     -- case-insensitive emails

-- Reusable trigger function to auto-maintain updated_at columns
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------
-- 1. Users  (Sales Reps / BDRs / Managers / Ops using the platform)
-- ---------------------------------------------------------------------
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           CITEXT NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,          -- store bcrypt/argon2 hash only
    role            VARCHAR(50)  NOT NULL DEFAULT 'sales_rep'
                        CHECK (role IN ('sales_rep','bdr','sales_manager','ops','admin')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- 2. Companies  (Prospect organizations)
-- ---------------------------------------------------------------------
CREATE TABLE companies (
    id               SERIAL PRIMARY KEY,
    name             VARCHAR(200) NOT NULL,
    industry         VARCHAR(100),
    website          VARCHAR(255),
    description      TEXT,
    employee_count   INTEGER CHECK (employee_count IS NULL OR employee_count >= 0),
    location         VARCHAR(150),
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (name, website)
);

CREATE TRIGGER trg_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------
-- 3. Leads  (Prospect / contact records — owned by a User, tied to a Company)
-- ---------------------------------------------------------------------
CREATE TABLE leads (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_id      INTEGER REFERENCES companies(id) ON DELETE SET NULL,
    name            VARCHAR(100) NOT NULL,
    email           CITEXT,
    phone           VARCHAR(20),
    company         VARCHAR(150),      -- denormalized display copy (kept for quick search / CSV import)
    industry        VARCHAR(100),
    status          VARCHAR(50) NOT NULL DEFAULT 'new'
                        CHECK (status IN ('new','contacted','qualified','proposal',
                                           'negotiation','closed_won','closed_lost')),
    score           INTEGER DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    source          VARCHAR(100),      -- e.g. LinkedIn, CSV Upload, Website Form, CRM
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX idx_leads_user_id     ON leads(user_id);
CREATE INDEX idx_leads_company_id  ON leads(company_id);
CREATE INDEX idx_leads_status      ON leads(status);
CREATE INDEX idx_leads_email       ON leads(email);

-- ---------------------------------------------------------------------
-- 4. Outreach_Campaigns  (AI-generated outreach messages per Lead)
-- ---------------------------------------------------------------------
CREATE TABLE outreach_campaigns (
    id              SERIAL PRIMARY KEY,
    lead_id         INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    subject         VARCHAR(255),
    message         TEXT NOT NULL,
    channel         VARCHAR(50) NOT NULL DEFAULT 'email'
                        CHECK (channel IN ('email','linkedin','sms','call','whatsapp')),
    sent_at         TIMESTAMP,
    status          VARCHAR(50) NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft','sent','opened','clicked','replied','bounced','failed')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_campaigns_lead_id ON outreach_campaigns(lead_id);
CREATE INDEX idx_campaigns_status  ON outreach_campaigns(status);

-- ---------------------------------------------------------------------
-- 5. Conversations  (Messages/interactions tied to a Lead & Campaign)
-- ---------------------------------------------------------------------
CREATE TABLE conversations (
    id              SERIAL PRIMARY KEY,
    lead_id         INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    campaign_id     INTEGER REFERENCES outreach_campaigns(id) ON DELETE SET NULL,
    sender          VARCHAR(50) NOT NULL CHECK (sender IN ('user','lead')),
    message         TEXT NOT NULL,
    sent_at         TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_lead_id     ON conversations(lead_id);
CREATE INDEX idx_conversations_campaign_id ON conversations(campaign_id);

-- ---------------------------------------------------------------------
-- 6. Lead_Scores  (AI scoring history — latest row = current score)
-- ---------------------------------------------------------------------
CREATE TABLE lead_scores (
    id              SERIAL PRIMARY KEY,
    lead_id         INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    score           INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    reason          TEXT,
    scored_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_lead_scores_lead_id  ON lead_scores(lead_id);
CREATE INDEX idx_lead_scores_scored_at ON lead_scores(lead_id, scored_at DESC);

-- ---------------------------------------------------------------------
-- 7. CRM_Sync_Logs  (Sync activity between SalesGenie and external CRMs)
-- ---------------------------------------------------------------------
CREATE TABLE crm_sync_logs (
    id              SERIAL PRIMARY KEY,
    lead_id         INTEGER NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    crm_name        VARCHAR(50) NOT NULL,             -- e.g. Salesforce, HubSpot, Zoho
    crm_record_id   VARCHAR(150),
    action          VARCHAR(50) NOT NULL CHECK (action IN ('create','update','delete')),
    status          VARCHAR(50) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','synced','failed')),
    synced_at       TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_crm_sync_lead_id ON crm_sync_logs(lead_id);
CREATE INDEX idx_crm_sync_status  ON crm_sync_logs(status);

-- ---------------------------------------------------------------------
-- 8. Convenience View — current (latest) lead score per lead
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_lead_current_score AS
SELECT DISTINCT ON (lead_id)
    lead_id,
    score,
    reason,
    scored_at
FROM lead_scores
ORDER BY lead_id, scored_at DESC;

-- =====================================================================
-- End of schema
-- =====================================================================
