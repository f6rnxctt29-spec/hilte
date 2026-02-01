AGENT POLICY

This document describes the agent policy configuration and safe defaults.

- auto_merge: PR-only | limited | full
- daily_hq_cap_usd: daily dollar cap for HQ model usage (default 5)
- max_auto_pushes_per_day: maximum automatic pushes per day (default 20)
- safe_paths: list of repository paths where agent may auto-commit without manual approval
- allow_pii_ops: whether agent may export or handle PII automatically (default false)
- allow_payments: whether agent may execute payment operations (default false)
- elevated_session_timeout_min: duration in minutes for temporary elevated mode

How to change:
- Edit agent/config.py and commit. Agent will reload policy on next task (or on restart).
- For risky operations (PII, payments), use one-time override token via Control UI. See /mcp/admin/override endpoint.

Approval flows:
- Telegram one-click approve: agent will post a summary card for blocked ops; pressing "Approve" authorizes the operation.
- One-time token: generated in Control UI; paste it into the override endpoint (not chat) to authorize a single blocked action.

Audit:
- All HQ usage, overrides and critical actions are logged to /Users/nickznatkov/.openclaw/workspace/logs/agent_model_usage.json and into audit_logs DB table with chain-hash.
