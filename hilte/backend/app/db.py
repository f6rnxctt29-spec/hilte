from __future__ import annotations

from contextlib import contextmanager
import os
import psycopg
from psycopg.rows import dict_row

@contextmanager
def get_conn():
    # Read from env at runtime so restarts/LaunchAgents pick it up correctly
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise RuntimeError('DATABASE_URL is not set')

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        yield conn
