# Agent policy/configuration

POLICY = {
    "auto_merge": "PR-only",  # PR-only | limited | full
    "daily_hq_cap_usd": 5,
    "max_auto_pushes_per_day": 20,
    "safe_paths": [],  # list of paths where agent may auto-commit
    "allow_pii_ops": False,  # requires one-time signed override via Control UI
    "allow_payments": False,  # immutable without Control UI override
    "elevated_session_timeout_min": 15,
}

# Loader placeholder (reloads can be implemented to watch file changes)
def get_policy():
    return POLICY
