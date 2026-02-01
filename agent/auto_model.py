"""Auto model selector for agent tasks.

Rules (simple heuristics):
- Short formatting / lint / tests / trivial edits -> mini
- Refactors / large generation / planning -> hq (respecting daily cap)
- Bulk embedding/graph tasks -> worker (cheap)

This module exposes select_model(task) and records HQ usage via audit hook.
"""
from datetime import datetime
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.py"
USAGE_LOG = Path("/Users/nickznatkov/.openclaw/workspace/logs/agent_model_usage.json")

# simple heuristics
HQ_TASK_KEYWORDS = ["refactor", "rewrite", "design", "plan", "architecture", "generate tests", "strategy"]
WORKER_TASK_KEYWORDS = ["embed", "embedding", "graph", "dry-run", "batch"]


def _load_policy():
    try:
        # import local config
        from .config import get_policy
        return get_policy()
    except Exception:
        return {"daily_hq_cap_usd": 5}


def _record_usage(entry: dict):
    try:
        USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
        data = []
        if USAGE_LOG.exists():
            data = json.loads(USAGE_LOG.read_text())
        data.insert(0, entry)
        # keep last 500
        data = data[:500]
        USAGE_LOG.write_text(json.dumps(data, default=str, indent=2))
    except Exception:
        pass


def select_model(task_text: str, estimated_cost_usd: float = 0.0) -> str:
    """Return model alias: 'mini' | 'hq' | 'worker' and record HQ use if chosen."""
    text = task_text.lower()
    policy = _load_policy()
    cap = policy.get("daily_hq_cap_usd", 5)

    # worker preference
    if any(k in text for k in WORKER_TASK_KEYWORDS):
        return "worker"

    # HQ preference
    if any(k in text for k in HQ_TASK_KEYWORDS):
        # check cap usage so far
        used = 0.0
        try:
            if USAGE_LOG.exists():
                data = json.loads(USAGE_LOG.read_text())
                for e in data:
                    if e.get("model") == "hq" and e.get("date","")[:10] == datetime.utcnow().isoformat()[:10]:
                        used += float(e.get("cost",0.0))
        except Exception:
            used = 0.0
        if used + estimated_cost_usd <= cap:
            entry = {"date": datetime.utcnow().isoformat(), "model": "hq", "cost": estimated_cost_usd, "task": task_text[:200]}
            _record_usage(entry)
            return "hq"
        else:
            # cap exceeded
            return "mini"

    # default
    return "mini"
