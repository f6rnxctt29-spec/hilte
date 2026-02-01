AGENT SCAFFOLD

This folder contains the scaffold for the autonomous agent (planner/executor/verifier/runner).

Files:
- planner.py  # LLM planner interface (calls to LLM are gated by policy)
- executor.py # executes local commands, applies patches, runs tests
- verifier.py # runs smoke checks (health endpoints, basic curl tests)
- runner.py   # task queue and scheduler
- config.py   # policy caps and safe lists
- AGENT_SPEC.md -> higher-level spec (see repo root)

NOTE: This scaffold does not include any secrets. GitHub access is performed via secure token from Control UI.
