create table if not exists missions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  status text,
  prompt text,
  context text,
  quote_cents integer,
  quote_currency text,
  quote_breakdown jsonb,
  stripe_session_id text,
  stripe_payment_intent_id text,
  paid_at timestamp with time zone,
  file_names text[],
  file_context text,
  gemini text,
  gpt text,
  claude text,
  grok text,
  evidence jsonb,
  governance jsonb,
  completed_at timestamp with time zone,
  metadata jsonb
);

create table if not exists audit_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  mission_id uuid references missions(id) on delete cascade,
  event_type text not null,
  payload jsonb
);

create index if not exists audit_events_mission_id_idx on audit_events (mission_id);

create table if not exists governance_policies (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  pattern text not null,
  severity text default 'medium',
  scope text default 'all',
  enabled boolean default true,
  metadata jsonb
);

create table if not exists governance_reviews (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  mission_id uuid references missions(id) on delete cascade,
  status text,
  score integer,
  violations jsonb,
  summary jsonb
);

create table if not exists compliance_reviews (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  mission_id uuid references missions(id) on delete cascade,
  status text,
  score integer,
  findings jsonb,
  summary jsonb
);

create table if not exists domain_profiles (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  description text,
  compliance_threshold integer default 80,
  trust_threshold integer default 70,
  consensus_threshold double precision default 0.25,
  required_certifications jsonb,
  policy_tags text[],
  metadata jsonb
);

create table if not exists domain_certifications (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  domain_id uuid references domain_profiles(id) on delete cascade,
  agent_name text,
  certification_level text,
  valid_from timestamp with time zone,
  valid_to timestamp with time zone,
  evidence jsonb,
  metadata jsonb
);

create table if not exists knowledge_packages (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  description text,
  category text,
  source text,
  url text,
  content_hash text,
  summary text,
  tags text[],
  metadata jsonb
);

create table if not exists domain_packages (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  domain_id uuid references domain_profiles(id) on delete cascade,
  package_id uuid references knowledge_packages(id) on delete cascade,
  package_name text,
  role text,
  priority integer default 1,
  metadata jsonb
);

create table if not exists compliance_templates (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  domain_id uuid references domain_profiles(id) on delete cascade,
  name text not null,
  validator_instructions text,
  policy_rules jsonb,
  severity text default 'high',
  tags text[],
  metadata jsonb
);

create table if not exists domain_badges (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  domain_id uuid references domain_profiles(id) on delete cascade,
  name text not null,
  description text,
  level text,
  criteria jsonb,
  metadata jsonb
);

create table if not exists certification_exams (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  domain_id uuid references domain_profiles(id) on delete cascade,
  title text not null,
  description text,
  pass_score integer default 85,
  certification_level text,
  rubric jsonb,
  questions jsonb,
  metadata jsonb
);

create table if not exists certification_exam_results (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  domain_id uuid references domain_profiles(id) on delete cascade,
  exam_id uuid references certification_exams(id) on delete cascade,
  agent_name text,
  score integer,
  status text,
  details jsonb
);

create table if not exists board_members (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  member_type text not null,
  role text,
  active boolean default true,
  metadata jsonb
);

create table if not exists board_terms (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  term_label text not null,
  start_date date,
  end_date date,
  status text default 'active',
  metadata jsonb
);

create table if not exists board_assignments (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  term_id uuid references board_terms(id) on delete cascade,
  member_id uuid references board_members(id) on delete cascade,
  seat text,
  responsibility text,
  active boolean default true,
  metadata jsonb
);

create table if not exists board_criteria (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  description text,
  category text,
  weight_default integer,
  is_active boolean default true,
  metadata jsonb
);

create table if not exists board_sessions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  term_id uuid references board_terms(id) on delete set null,
  mission_id uuid references missions(id) on delete set null,
  domain_id uuid references domain_profiles(id) on delete set null,
  title text,
  criteria_commit text,
  criteria_payload jsonb,
  revealed_at timestamp with time zone,
  metadata jsonb
);

create table if not exists board_scores (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  session_id uuid references board_sessions(id) on delete cascade,
  member_id uuid references board_members(id) on delete set null,
  score integer,
  notes text,
  criteria_scores jsonb,
  metadata jsonb
);

create table if not exists ledger_events (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  event_type text not null,
  amount_cents integer default 0,
  currency text,
  mission_id uuid references missions(id) on delete set null,
  metadata jsonb,
  event_hash text
);

create table if not exists ledger_anchors (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  period_start date,
  period_end date,
  ledger_hash text,
  tx_hash text,
  status text default 'pending',
  metadata jsonb
);

create table if not exists monthly_audits (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  month_label text,
  status text default 'open',
  summary jsonb,
  ledger_anchor_id uuid references ledger_anchors(id) on delete set null,
  metadata jsonb
);

create table if not exists connectors (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  connector_type text,
  description text,
  status text default 'inactive',
  edge_url text,
  scopes jsonb,
  config jsonb,
  metadata jsonb
);

create index if not exists connectors_name_idx
  on connectors (name);

create table if not exists connector_runs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  connector_id uuid references connectors(id) on delete cascade,
  status text,
  request_payload jsonb,
  response_payload jsonb,
  response_status integer,
  error text,
  metadata jsonb
);

create index if not exists connector_runs_connector_id_idx
  on connector_runs (connector_id);

create table if not exists document_uploads (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  file_name text,
  file_path text,
  file_size integer,
  mime_type text,
  sha256 text,
  metadata jsonb
);

create index if not exists document_uploads_sha256_idx
  on document_uploads (sha256);

create table if not exists governance_protocols (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  cadence text,
  scope text,
  description text,
  human_roles jsonb,
  ai_roles jsonb,
  steps jsonb,
  evidence_requirements jsonb,
  escalation jsonb,
  metadata jsonb
);

create index if not exists governance_protocols_name_idx
  on governance_protocols (name);

create table if not exists evolution_playbooks (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  description text,
  stages jsonb,
  guardrails jsonb,
  required_metrics jsonb,
  approval_chain jsonb,
  metadata jsonb
);

create index if not exists evolution_playbooks_name_idx
  on evolution_playbooks (name);

create table if not exists agent_tiers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  tier_level integer,
  description text,
  min_usd integer,
  max_usd integer,
  required_certifications jsonb,
  required_badges jsonb,
  autonomy_level text,
  allowed_domains jsonb,
  review_requirements jsonb,
  metadata jsonb
);

create index if not exists agent_tiers_name_idx
  on agent_tiers (name);

create table if not exists bot_task_tiers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  name text not null,
  tier_level integer,
  description text,
  min_usd integer,
  max_usd integer,
  allowed_sources jsonb,
  task_types jsonb,
  risk_controls jsonb,
  evidence_requirements jsonb,
  metadata jsonb
);

create index if not exists bot_task_tiers_name_idx
  on bot_task_tiers (name);

create table if not exists document_registry (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  source_repo text,
  file_path text,
  file_extension text,
  bucket text,
  size_bytes integer,
  modified_at timestamp with time zone,
  sha256 text,
  excerpt jsonb,
  metadata jsonb
);

create table if not exists domain_documents (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  domain_id uuid references domain_profiles(id) on delete cascade,
  document_id uuid references document_registry(id) on delete cascade,
  file_path text,
  sha256 text,
  excerpt jsonb,
  tags text[],
  metadata jsonb
);

create table if not exists document_taxonomy (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  document_id uuid references document_registry(id) on delete cascade,
  label text,
  category text,
  confidence double precision,
  tags text[],
  metadata jsonb
);

create index if not exists document_taxonomy_document_id_idx
  on document_taxonomy (document_id);

create table if not exists evolution_proposals (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  title text not null,
  description text,
  rationale text,
  status text default 'pending',
  payload jsonb,
  approved_at timestamp with time zone,
  applied_at timestamp with time zone
);

create table if not exists evolution_runs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  iterations integer,
  result jsonb,
  status jsonb,
  signature text,
  metadata jsonb
);

create table if not exists academy_modules (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  title text not null,
  summary text,
  level text,
  status text default 'active',
  content jsonb,
  tags text[],
  metadata jsonb
);

create table if not exists deployments (
  id uuid primary key default gen_random_uuid(),
  created_at timestamp with time zone default now(),
  version text,
  environment text,
  status text,
  artifacts jsonb,
  notes text
);
