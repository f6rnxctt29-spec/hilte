-- DDL: incidents, audit_logs, triggers, trigger_logs
BEGIN;

-- incidents
CREATE TABLE IF NOT EXISTS incidents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID REFERENCES orders(id) ON DELETE SET NULL,
  reporter_id UUID REFERENCES staff(id) ON DELETE SET NULL,
  severity TEXT,
  status TEXT DEFAULT 'open',
  text TEXT,
  resolution TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor TEXT,
  action TEXT,
  target_table TEXT,
  target_id UUID,
  meta JSONB DEFAULT '{}'::jsonb,
  ts TIMESTAMPTZ DEFAULT now()
);

-- triggers
CREATE TABLE IF NOT EXISTS triggers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  condition JSONB DEFAULT '{}'::jsonb,
  cooldown_seconds INT DEFAULT 3600,
  suppressed BOOLEAN DEFAULT false,
  last_fired_at TIMESTAMPTZ
);

-- trigger_logs
CREATE TABLE IF NOT EXISTS trigger_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  trigger_id UUID REFERENCES triggers(id) ON DELETE CASCADE,
  status TEXT,
  result JSONB DEFAULT '{}'::jsonb,
  ran_at TIMESTAMPTZ DEFAULT now()
);

COMMIT;
