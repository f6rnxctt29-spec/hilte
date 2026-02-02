-- v1 core: process-first tables for HILTE CRM/ERP
BEGIN;

-- Immutable order timeline (juridical log)
CREATE TABLE IF NOT EXISTS order_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  actor text NOT NULL,
  action text NOT NULL,
  reason text NULL,
  meta jsonb DEFAULT '{}'::jsonb,
  ts timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_order_events_order_ts ON order_events(order_id, ts DESC);

-- Service formats (structured, rule-based)
CREATE TABLE IF NOT EXISTS service_formats (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text UNIQUE NOT NULL,
  name text NOT NULL,
  rules jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Add-on catalog (structured works)
CREATE TABLE IF NOT EXISTS service_addons (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text UNIQUE NOT NULL,
  name text NOT NULL,
  std_price numeric DEFAULT 0,
  std_cost numeric DEFAULT 0,
  margin_impact numeric DEFAULT 0,
  can_be_compliment boolean DEFAULT false,
  per_order_limit int DEFAULT 1,
  approval_level text DEFAULT 'manager',
  constraints jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Order items (base works + addons). Totals should be derived.
CREATE TABLE IF NOT EXISTS order_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  code text NOT NULL,
  name text NULL,
  qty numeric DEFAULT 1,
  price numeric DEFAULT 0,
  cost numeric DEFAULT 0,
  kind text DEFAULT 'base', -- base|addon
  is_compliment boolean DEFAULT false,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);

-- Trigger execution log
CREATE TABLE IF NOT EXISTS trigger_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  trigger_id uuid NULL REFERENCES triggers(id) ON DELETE SET NULL,
  name text NOT NULL,
  status text NOT NULL, -- fired|skipped|error
  result jsonb DEFAULT '{}'::jsonb,
  ran_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_trigger_logs_ran ON trigger_logs(ran_at DESC);

-- Compliments (not discounts): managed service expense
CREATE TABLE IF NOT EXISTS compliments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  type text NOT NULL,
  reason text NOT NULL,
  approval_level text DEFAULT 'manager',
  approved_by text NULL,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_compliments_order ON compliments(order_id);

-- ERP core (minimal stubs)
CREATE TABLE IF NOT EXISTS invoices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  number text NULL,
  amount numeric DEFAULT 0,
  status text DEFAULT 'draft', -- draft|issued|void
  issued_at timestamptz NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS payments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id uuid NULL REFERENCES invoices(id) ON DELETE SET NULL,
  order_id uuid NULL REFERENCES orders(id) ON DELETE SET NULL,
  amount numeric DEFAULT 0,
  method text NULL,
  status text DEFAULT 'received',
  received_at timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

-- Cost lines (detailed cost by category)
CREATE TABLE IF NOT EXISTS cost_lines (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id uuid NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  category text NOT NULL, -- labor|supplies|logistics|equipment|compliment|other
  amount numeric DEFAULT 0,
  meta jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

COMMIT;
