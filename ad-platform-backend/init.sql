-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create default admin user (password: Admin123!)
INSERT INTO "User" (id, email, username, password_hash, full_name, role, email_verified, is_active, created_at, updated_at)
VALUES 
  (uuid_generate_v4(), 'admin@adplatform.com', 'admin', '$2b$10$YourBcryptHashHere', 'Administrator', 'admin', true, true, NOW(), NOW())
ON CONFLICT (email) DO NOTHING;

-- Create default membership plans
INSERT INTO "MembershipPlan" (id, name, description, price, currency, duration_days, features, is_active, sort_order, max_ads, max_budget, created_at)
VALUES 
  (uuid_generate_v4(), 'Free', 'Basic access with limited features', 0.00, 'USD', 30, '["3 ads limit", "Basic analytics", "Email support"]', true, 1, 3, 100, NOW()),
  (uuid_generate_v4(), 'Pro', 'Professional features for growing businesses', 29.99, 'USD', 30, '["50 ads limit", "Advanced analytics", "Priority support", "A/B testing", "Custom targeting"]', true, 2, 50, 5000, NOW()),
  (uuid_generate_v4(), 'Enterprise', 'Full platform access with premium support', 99.99, 'USD', 30, '["Unlimited ads", "Real-time analytics", "24/7 support", "Custom integrations", "Dedicated account manager", "API access"]', true, 3, 9999, 50000, NOW())
ON CONFLICT DO NOTHING;

-- Create default system configurations
INSERT INTO "SystemConfig" (id, key, value, description, is_public, created_at, updated_at)
VALUES 
  (uuid_generate_v4(), 'site_name', 'Ad Platform', 'Website name', true, NOW(), NOW()),
  (uuid_generate_v4(), 'site_description', 'Premium advertising platform for businesses', 'Website description', true, NOW(), NOW()),
  (uuid_generate_v4(), 'currency', 'USD', 'Default currency', true, NOW(), NOW()),
  (uuid_generate_v4(), 'ad_review_required', 'true', 'Whether ads need manual review', false, NOW(), NOW()),
  (uuid_generate_v4(), 'max_file_size_mb', '5', 'Maximum file upload size in MB', true, NOW(), NOW()),
  (uuid_generate_v4(), 'support_email', 'support@adplatform.com', 'Support email address', true, NOW(), NOW()),
  (uuid_generate_v4(), 'telegram_support_link', 'https://t.me/adplatform_support', 'Telegram support link', true, NOW(), NOW())
ON CONFLICT (key) DO NOTHING;