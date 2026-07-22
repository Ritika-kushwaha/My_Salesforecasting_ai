-- =====================================================================
-- SalesGenie AI — Sample Seed Data (for dev/testing only)
-- =====================================================================

INSERT INTO users (name, email, password, role) VALUES
('Priya Sharma', 'priya.sharma@salesgenie.ai', '$2b$12$hashedpasswordplaceholder1', 'sales_rep'),
('Rahul Verma',  'rahul.verma@salesgenie.ai',  '$2b$12$hashedpasswordplaceholder2', 'sales_manager');

INSERT INTO companies (name, industry, website, description, employee_count, location) VALUES
('TechCorp Solutions', 'Enterprise Software', 'https://techcorp.example.com',
 'Series C enterprise software company scaling data infrastructure.', 350, 'San Francisco, CA'),
('InnovateAI Labs', 'AI/ML', 'https://innovateai.example.com',
 'Mid-market AI product company.', 120, 'Austin, TX');

INSERT INTO leads (user_id, company_id, name, email, phone, company, industry, status, score, source) VALUES
(1, 1, 'Sarah Johnson', 'sarah.johnson@techcorp.example.com', '+1-415-555-0101',
 'TechCorp Solutions', 'Enterprise Software', 'qualified', 92, 'LinkedIn'),
(1, 2, 'Mark Chen', 'mark.chen@innovateai.example.com', '+1-512-555-0199',
 'InnovateAI Labs', 'AI/ML', 'new', 68, 'Website Form');

INSERT INTO outreach_campaigns (lead_id, subject, message, channel, sent_at, status) VALUES
(1, 'Transform Your Data Pipeline with AI',
 'Hi Sarah, I noticed TechCorp recently secured Series C funding...', 'email', NOW() - INTERVAL '3 days', 'opened');

INSERT INTO conversations (lead_id, campaign_id, sender, message, sent_at) VALUES
(1, 1, 'lead', 'Thanks for reaching out — can you share more on integration capabilities?', NOW() - INTERVAL '2 days'),
(1, 1, 'user', 'Absolutely, sending over our technical architecture doc now.', NOW() - INTERVAL '2 days');

INSERT INTO lead_scores (lead_id, score, reason, scored_at) VALUES
(1, 85, 'Initial qualification based on company profile.', NOW() - INTERVAL '5 days'),
(1, 92, 'Score increased after positive email engagement and Series C signal.', NOW() - INTERVAL '1 day');

INSERT INTO crm_sync_logs (lead_id, crm_name, crm_record_id, action, status, synced_at) VALUES
(1, 'Salesforce', 'SF-00123', 'create', 'synced', NOW() - INTERVAL '4 days'),
(1, 'Salesforce', 'SF-00123', 'update', 'synced', NOW() - INTERVAL '1 day');
